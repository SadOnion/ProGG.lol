from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QRunnable

import threading

from lcu_driver import Connector
from summoner import Summoner
from messages import Messages


class WorkerSignals(QObject):
    result = pyqtSignal(object)


class LCU(QRunnable):
    def __init__(self):
        super(LCU, self).__init__()

        self.signals = WorkerSignals()

        self.summoners = {}
        self.lobby = {}

        self.summonersLock = threading.RLock()

        self.connector = Connector()
        self.connector.open(self.lcu_ready)
        self.connector.close(self.lcu_close)
        self.connector.ws.register(
            '/lol-gameflow/v1/gameflow-phase', event_types=('UPDATE',))(self.gameflow)

        self.connector.ws.register(
            '/lol-champ-select/v1/session', event_types=('UPDATE',))(self.champSelect)

    @pyqtSlot()
    def run(self):
        self.connector.start()

    async def lcu_ready(self, connection):
        self.signals.result.emit((Messages.LCU_CONNECTED,))

    async def lcu_close(self, _):
        self.signals.result.emit((Messages.LCU_DISCONNECTED,))

    async def gameflow(self, connection, event):
        print(str(event.data))
        if event.data == "ChampSelect":
            self.summoners = {}
            self.myTeamBans = []
            self.theirTeamBans = []
            self.signals.result.emit((Messages.CHAMPSELECT_ENTERED,))

        elif event.data == 'Matchmaking':
            if self.summoners is not {}:
                ourTeam = []
                theirTeam = []

                for k, s in self.summoners.items():
                    if s.champId == 0:
                        continue

                    if s.ourTeam:
                        ourTeam.append(s.champId)
                    else:
                        theirTeam.append(s.champId)

                self.summoners = {}

                self.signals.result.emit(
                    (Messages.SAVE_LOBBY, (ourTeam, theirTeam, self.myTeamBans, self.theirTeamBans)))

        elif event.data == "GameStart":
            ourTeam = []
            theirTeam = []

            for k, s in self.summoners.items():
                if s.champId == 0:
                    continue

                if s.ourTeam:
                    ourTeam.append(s.champId)
                else:
                    theirTeam.append(s.champId)

                self.summoners = {}

            self.signals.result.emit(
                (Messages.SAVE_LOBBY, (ourTeam, theirTeam, self.myTeamBans, self.theirTeamBans)))
            self.signals.result.emit((Messages.GAME_ENTERED,))

        elif event.data == "None":
            if self.summoners is not {}:
                ourTeam = []
                theirTeam = []

                for k, s in self.summoners.items():
                    if s.champId == 0:
                        continue

                    if s.ourTeam:
                        ourTeam.append(s.champId)
                    else:
                        theirTeam.append(s.champId)

                self.summoners = {}

                self.signals.result.emit(
                    (Messages.SAVE_LOBBY, (ourTeam, theirTeam, self.myTeamBans, self.theirTeamBans)))

            # self.signals.result.emit((Messages.CHAMPSELECT_QUIT,))

    async def champSelect(self, connection, event):
        myTeam = event.data['myTeam']
        theirTeam = event.data['theirTeam']

        bans = event.data['bans']
        self.myTeamBans = bans['myTeamBans']
        self.theirTeamBans = bans['theirTeamBans']

        champId = 0

        # bans': {'myTeamBans': [523, 63], 'numBans': 6, 'theirTeamBans': [82, 147]},

        with self.summonersLock:
            for i, c in enumerate(myTeam):
                if c['championPickIntent'] == 0:
                    champId = c['championId']
                else:
                    champId = c['championPickIntent']

                summonerId = c['summonerId']

                if summonerId not in self.summoners:
                    self.summoners[summonerId] = Summoner(i, True, connection,
                                                          summonerId, self.signals.result)

                else:
                    if self.summoners[summonerId].champId != champId:
                        self.summoners[summonerId].setChamp(champId)

            for i, c in enumerate(theirTeam):
                if c['championPickIntent'] == 0:
                    champId = c['championId']
                else:
                    champId = c['championPickIntent']

                summonerId = c['summonerId']

                if summonerId not in self.summoners:
                    self.summoners[summonerId] = Summoner(i, False, connection,
                                                          summonerId, self.signals.result)

                else:
                    if self.summoners[summonerId].champId != champId:
                        self.summoners[summonerId].setChamp(champId)
