from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QRunnable

import threading
import asyncio

from lolapi import lolapi
from lcu_driver import Connector
from messages import Messages
from championSelect import ChampionSelect
from player import Player
import itertools


class LCUSignals(QObject):
    result = pyqtSignal(object)


class LCU(QRunnable):
    def __init__(self):
        super(LCU, self).__init__()

        self.signals = LCUSignals()

        self.beenInChampSelect = False

        self.champSelectLock = asyncio.Lock()

        # self.rockPaperScissorsBot = False

        self.connector = Connector()
        self.connector.open(self.lcu_ready)
        self.connector.close(self.lcu_close)
        self.connector.ws.register(
            '/lol-gameflow/v1/gameflow-phase', event_types=('UPDATE',))(self.gameflowChanged)

        self.connector.ws.register(
            '/lol-champ-select/v1/session', event_types=('UPDATE',))(self.championSelectChanged)

    @pyqtSlot()
    def run(self):
        self.connector.start()

    async def lcu_ready(self, connection):
        summoner = await connection.request('get', '/lol-platform-config/v1/namespaces/LoginDataPacket/platformId')

        if summoner.status == 200:
            region = await summoner.json()
            if region == 'EUN1':
                lolapi.set_default_region('EUNE')
            elif region == 'EUW1':
                lolapi.set_default_region('EUW')
            else:
                print('UNSUPPORTED REGION')
                return

            self.signals.result.emit((Messages.LCU_CONNECTED,))

            phase = await connection.request('get', '/lol-gameflow/v1/gameflow-phase')

            if phase.status == 200:
                event = type("", (), dict(data=await phase.json()))()
                await self.gameflowChanged(connection, event)

    async def lcu_close(self, _):
        self.signals.result.emit((Messages.LCU_DISCONNECTED,))

    async def gameflowChanged(self, connection, event):
        print(f"gameflow status: {event.data}")

        if event.data == "ChampSelect":
            self.signals.result.emit((Messages.CHAMPSELECT_ENTERED,))
        else:
            if self.beenInChampSelect:
                self.beenInChampSelect = False
                self.signals.result.emit(
                    (Messages.CHAMPSELECT_SAVE, self.championSelect))

        if event.data == "InProgress":
            self.signals.result.emit(
                (Messages.GAME_STARTED,))
        elif event.data == "None" or event.data == "Lobby":
            self.signals.result.emit((Messages.NONE,))

    async def fetchSummoner(self, connection, summonerId):
        summoner = await connection.request('get', '/lol-summoner/v1/summoners/{}'.format(summonerId))

        if summoner.status == 200:
            json = await summoner.json()
            return json['displayName'], json['puuid']

    async def championSelectChanged(self, connection, event):
        myTeam = event.data['myTeam']
        theirTeam = event.data['theirTeam']

        async with self.champSelectLock:
            updated = False

            if not self.beenInChampSelect:
                players = {}
                for player in myTeam + theirTeam:
                    name = ''
                    puuid = ''

                    if player['summonerId'] != 0:
                        name, puuid = await self.fetchSummoner(connection, player['summonerId'])

                    players[player['cellId']] = Player(
                        name, puuid, player['team'], player['assignedPosition'])

                me = await connection.request('get', '/lol-summoner/v1/current-summoner')
                if me.status == 200:
                    json = await me.json()

                    self.championSelect = ChampionSelect(
                        players, json['displayName'])
                    self.beenInChampSelect = True
                    updated = True

            actions = itertools.chain(*event.data['actions'])
            for action in actions:
                if action['type'] == 'ban' and action['completed']:
                    updated = self.championSelect.setPlayerBannedChampion(
                        action['actorCellId'], action['id'], action['championId'])

            champId = 0
            for player in myTeam + theirTeam:
                if player['championPickIntent'] == 0:
                    champId = player['championId']
                else:
                    champId = player['championPickIntent']

                if champId != 0:
                    changed = await self.championSelect.setPlayerChampion(
                        player['cellId'], champId)

                    if not updated and changed:
                        updated = True

            if updated:
                self.signals.result.emit(
                    (Messages.CHAMPSELECT_UPDATED, self.championSelect))
