from PyQt5 import QtWidgets, uic

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from PIL.ImageQt import ImageQt

import sys
import lcu_driver
import os
import asyncio

import datetime
from cass import *


from lcu import LCU

from messages import Messages


qt_creator_file = "mainwindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_creator_file)


class TeamModel(QAbstractTableModel):
    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.parent = parent
        self.summoners = [None] * 5

    def rowCount(self, parent):
        return len(self.summoners)

    def columnCount(self, parent):
        return 5

    def setData(self, i, summoner):
        self.summoners[i] = summoner

    def data(self, index, role):
        summoner = self.summoners[index.row()]

        if summoner:
            if role == Qt.DisplayRole:
                if index.column() == 0:
                    if summoner.champImage is None:
                        return QVariant(summoner.champName)
                elif index.column() == 1:
                    return QVariant(summoner.name)
                elif index.column() == 2:
                    return QVariant(summoner.rank)
                else:
                    return QVariant('')
            elif role == Qt.DecorationRole:
                if index.column() == 0:
                    if summoner.champImage is not None:
                        qim = ImageQt(summoner.champImage)
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


class LobbyView(QWidget):

    def __init__(self, lobby):
        super().__init__()

        self.lobby = lobby

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.setMinimumWidth(440)

    def paintEvent(self, e):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(QPen(Qt.red, 3))

        i = 0

        for c in self.lobby[0]:

            qim = ImageQt(cass.Champion(id=c).image.image)
            qim = qim.scaled(40, 40, Qt.KeepAspectRatio)

            painter.drawImage(QPoint(qim.width() * i, 0), qim)

            i += 1

        i = 0

        for c in self.lobby[2]:
            qim = ImageQt(cass.Champion(id=c).image.image)
            qim = qim.scaled(40, 40, Qt.KeepAspectRatio)
            painter.drawImage(
                QPoint(qim.width() * i, qim.height()), qim)

            painter.drawLine(qim.width() * i, qim.height(),
                             qim.width() * (i + 1), qim.height() * 2)
            painter.drawLine(qim.width() * (i + 1), qim.height(),
                             qim.width() * i, qim.height() * 2)

            i += 1

        theirTeamOffset = max(len(self.lobby[0]), len(self.lobby[1])) + 1

        i = theirTeamOffset
        for c in self.lobby[1]:

            qim = ImageQt(cass.Champion(id=c).image.image)
            qim = qim.scaled(40, 40, Qt.KeepAspectRatio)

            painter.drawImage(QPoint(qim.width() * i, 0), qim)

            i += 1

        i = theirTeamOffset
        for c in self.lobby[3]:
            qim = ImageQt(cass.Champion(id=c).image.image)
            qim = qim.scaled(40, 40, Qt.KeepAspectRatio)
            painter.drawImage(
                QPoint(qim.width() * i, qim.height()), qim)

            painter.drawLine(qim.width() * i, qim.height(),
                             qim.width() * (i + 1), qim.height() * 2)
            painter.drawLine(qim.width() * (i + 1), qim.height(),
                             qim.width() * i, qim.height() * 2)

            i += 1

        painter.end()


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # tmp
        self.stackedWidget.setCurrentIndex(1)

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

        self.lobbies = []

    def handle_msg(self, msg):
        print(msg)

        msgType = msg[0]

        if msgType == Messages.LCU_CONNECTED:
            self.waitingLabel.setText('Waiting for champion select')
        elif msgType == Messages.LCU_DISCONNECTED:
            self.waitingLabel.setText('Waiting for league client')
        elif msgType == Messages.CHAMPSELECT_ENTERED:
            self.stackedWidget.setCurrentIndex(1)
        elif msgType == Messages.CHAMPSELECT_QUIT:
            self.stackedWidget.setCurrentIndex(0)
        elif msgType == Messages.CHAMPSELECT_UPDATED:
            summ = msg[1]
            if summ.ourTeam:
                self.ourTeamTableModel.setData(summ.lobbyPos, summ)
                self.ourTeamTableModel.layoutChanged.emit()
            else:
                self.theirTeamTableModel.setData(summ.lobbyPos, summ)
                self.theirTeamTableModel.layoutChanged.emit()
        elif msgType == Messages.SAVE_LOBBY:
            lobby = msg[1]

            y = self.previousLobbiesGrid.layout().columnCount()

            label = QLabel(datetime.datetime.now().strftime('%H:%M:%S'))
            label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            label.setAlignment(Qt.AlignHCenter)
            drawingView = LobbyView(lobby)

            self.previousLobbiesGrid.layout().addWidget(
                label, 0, y)
            self.previousLobbiesGrid.layout().addWidget(drawingView, 1, y)

            self.lobbies.insert(0, lobby)


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
