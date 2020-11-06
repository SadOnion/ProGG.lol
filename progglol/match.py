from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QRunnable

from lolapi import lolapi
from liveapi import request
from messages import Messages
from player import Player

import time


class MatchSignals(QObject):
    result = pyqtSignal(object)


class Match(QRunnable):

    def __init__(self):
        super(Match, self).__init__()

        self.signals = MatchSignals()

    @pyqtSlot()
    def run(self):
        playerlist = None

        while not playerlist:
            try:
                playerlist = request('playerlist')
            except:
                pass

            time.sleep(0.5)

        self.players = {}

        for player in playerlist.json():
            summonerName = player['summonerName']
            team = 0
            if player['team'] == 'ORDER':
                team = 1
            else:
                team = 2

            self.players[summonerName] = Player(
                summonerName, '', team, player['position'])

            self.players[summonerName].champion = lolapi.Champion(
                name=player['championName'])

        self.signals.result.emit((Messages.GAME_UPDATED, self))

    def getTeam(self, teamId):
        ret = []
        for player in self.players.values():
            if player.team == teamId:
                ret.append(player)

        return ret
