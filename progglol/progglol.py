from PyQt5 import QtWidgets, uic

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from PIL.ImageQt import ImageQt

import stat
import winreg
import sys
import lcu_driver
import os
import asyncio

import datetime


from lcu import LCU

from messages import Messages


REG_PATH = r"SOFTWARE\WOW6432Node\Riot Games, Inc\League of Legends"
REG_KEY = r"Location"

LOL_CONFIG_SUBPATH = "\\Config\\"


qt_creator_file = "mainwindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_creator_file)


class TeamModel(QAbstractTableModel):
    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.parent = parent
        self.team = []

    def rowCount(self, parent):
        return len(self.team)

    def columnCount(self, parent):
        return 5

    def setData(self, team):
        self.team = team

    def data(self, index, role):
        player = self.team[index.row()]

        if role == Qt.DisplayRole:
            if index.column() == 1:
                return QVariant(player.summonerName)
            elif index.column() == 2:
                return QVariant(player.getRank())
            else:
                return QVariant('')
        elif role == Qt.DecorationRole:
            if index.column() == 0:
                if player.champion:
                    qim = ImageQt(player.champion.image.image)
                    qim = qim.scaled(self.parent.columnWidth(
                        index.column()), self.parent.rowHeight(index.row()), Qt.KeepAspectRatio)
                    pix = QPixmap.fromImage(qim)
                    return pix

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignVCenter + Qt.AlignHCenter

    def headerData(self, section, orientation, role):
        header = ['Champion', 'Nick', 'Rank', '', '']

        if role == Qt.DisplayRole:
            return header[section]


class ChampionSelectView(QWidget):

    def __init__(self, championSelect):
        super().__init__()

        self.championSelect = championSelect

        team1Size = len(championSelect.getTeam(1))
        for player in championSelect.getTeam(1):
            team1Size = max(team1Size, len(player.bannedChampions))

        team2Size = len(championSelect.getTeam(2))
        for player in championSelect.getTeam(2):
            team2Size = max(team2Size, len(player.bannedChampions))

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setMinimumWidth((team1Size + team2Size + 2) * 40)

        print(self.minimumWidth())

    def paintTeam(self, painter, team, xOffset):
        pickXOffset = xOffset
        banXOffset = xOffset

        for player in self.championSelect.getTeam(team):
            if player.champion:
                qim = ImageQt(player.champion.image.image)
                qim = qim.scaled(40, 40, Qt.KeepAspectRatio)

                painter.drawImage(QPoint(qim.width() * pickXOffset, 0), qim)

                pickXOffset += 1

            for champion in player.bannedChampions.values():
                qim = ImageQt(champion.image.image)
                qim = qim.scaled(40, 40, Qt.KeepAspectRatio)

                painter.drawImage(
                    QPoint(qim.width() * banXOffset, qim.height()), qim)

                painter.drawLine(qim.width() * banXOffset, qim.height(),
                                 qim.width() * (banXOffset + 1), qim.height() * 2)
                painter.drawLine(qim.width() * (banXOffset + 1), qim.height(),
                                 qim.width() * banXOffset, qim.height() * 2)

                banXOffset += 1

        return max(pickXOffset, banXOffset)

    def paintEvent(self, e):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(QPen(Qt.red, 3))

        xOffset = self.paintTeam(painter, 1, 0)
        xOffset += 1
        self.paintTeam(painter, 2, xOffset)

        painter.end()


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # tmp
        self.stackedWidget.setCurrentIndex(1)

        registry_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, REG_PATH, 0, winreg.KEY_READ)
        leaguePath, regtype = winreg.QueryValueEx(registry_key, REG_KEY)
        winreg.CloseKey(registry_key)

        self.settingsFilePath = leaguePath + '\\Config\\PersistedSettings.json'

        if self.isSettingsReadOnly():
            self.lockSettingsButton.setText('Unlock settings')
        else:
            self.lockSettingsButton.setText('Lock settings')

        self.lockSettingsButton.clicked.connect(
            self.toggleSettingsReadOnly)

        self.rockPaperScissorsButton.clicked.connect(
            self.toggleRockPaperScissorsBot)

        self.ourTeamTableModel = TeamModel(self.ourTeamTable)
        self.ourTeamTable.setModel(self.ourTeamTableModel)
        self.ourTeamTable.verticalHeader().setVisible(False)
        self.ourTeamTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.theirTeamTableModel = TeamModel(self.theirTeamTable)
        self.theirTeamTable.setModel(self.theirTeamTableModel)
        self.theirTeamTable.verticalHeader().setVisible(False)
        self.theirTeamTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.threadpool = QThreadPool()

        self.lcu = LCU()
        self.lcu.signals.result.connect(self.handle_msg)
        self.threadpool.start(self.lcu)

    def isSettingsReadOnly(self):
        return os.stat(self.settingsFilePath).st_mode & stat.S_IWRITE != stat.S_IWRITE

    @pyqtSlot()
    def toggleSettingsReadOnly(self):
        print('toggling')
        st_mode = os.stat(self.settingsFilePath).st_mode
        os.chmod(self.settingsFilePath, st_mode ^ stat.S_IWRITE)

        if self.isSettingsReadOnly():
            self.lockSettingsButton.setText('Unlock settings')
        else:
            self.lockSettingsButton.setText('Lock settings')

    @pyqtSlot()
    def toggleRockPaperScisssorsBot(self):
        if self.lcu.rockPaperScissorsBot:
            self.lcu.rockPaperScissorsBot = False
            self.rockPaperScissorsButton.setText('Enable')
        else:
            self.lcu.rockPaperScissorsBot = True
            self.rockPaperScissorsButton.setText('Disable')

    def handle_msg(self, msg):
        print(msg)

        msgType = msg[0]

        if msgType == Messages.LCU_CONNECTED:
            self.stackedWidget.setCurrentIndex(1)
        elif msgType == Messages.LCU_DISCONNECTED:
            self.stackedWidget.setCurrentIndex(0)
        elif msgType == Messages.CHAMPSELECT_ENTERED:
            self.stackedWidget.setCurrentIndex(2)
        elif msgType == Messages.CHAMPSELECT_QUIT:
            self.stackedWidget.setCurrentIndex(1)
        elif msgType == Messages.CHAMPSELECT_UPDATED:
            champSelect = msg[1]
            self.ourTeamTableModel.setData(champSelect.getTeam(1))
            self.ourTeamTableModel.layoutChanged.emit()

            self.theirTeamTableModel.setData(champSelect.getTeam(2))
            self.theirTeamTableModel.layoutChanged.emit()
        elif msgType == Messages.CHAMPSELECT_SAVE:
            champSelect = msg[1]

            y = self.previousLobbiesGrid.layout().columnCount()

            label = QLabel(datetime.datetime.now().strftime('%H:%M:%S'))
            label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            label.setAlignment(Qt.AlignHCenter)
            champSelectView = ChampionSelectView(champSelect)

            self.previousLobbiesGrid.layout().addWidget(
                label, 0, y)
            self.previousLobbiesGrid.layout().addWidget(champSelectView, 1, y)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


""" 
champions = cass.get_champions()


summoner = cass.Summoner(name="rdκ")
print(summoner)
"""
