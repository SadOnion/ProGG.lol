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
            self.signals.result.emit((Messages.ENTERED_CHAMPSELECT,))
        elif event.data == "None":
            self.signals.result.emit((Messages.QUIT_CHAMPSELECT,))

    async def champSelect(self, connection, event):
        myTeam = event.data['myTeam']
        theirTeam = event.data['theirTeam']

        champId = 0

        with self.summonersLock:
            for i, c in enumerate(myTeam + theirTeam):
                if c['championPickIntent'] == 0:
                    champId = c['championId']
                else:
                    champId = c['championPickIntent']

                summonerId = c['summonerId']

                if summonerId not in self.summoners:
                    self.summoners[summonerId] = Summoner(i, connection,
                                                          summonerId, self.signals.result)

                elif self.summoners[summonerId].champId != champId:
                    self.summoners[summonerId].setChamp(champId)
