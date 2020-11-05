from PyQt5 import QtWidgets, uic

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from PIL.ImageQt import ImageQt

import sys
import lcu_driver
import os
import asyncio


from lcu import LCU

from messages import Messages


qt_creator_file = "mainwindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_creator_file)


class TeamModel(QAbstractTableModel):
    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.parent = parent
        self.summoners = []

    def rowCount(self, parent):
        return len(self.summoners)

    def columnCount(self, parent):
        return 5

    def setData(self, i, summoner):
        if len(self.summoners) == i:
            self.summoners.append(summoner)
        else:
            self.summoners[i] = summoner

    def data(self, index, role):
        summoner = self.summoners[index.row()]
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
                    pix = QPixmap.fromImage(qim)
                    return pix.scaled(self.parent.columnWidth(index.column()), self.parent.rowHeight(index.row()), Qt.KeepAspectRatio)
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignVCenter + Qt.AlignHCenter

    def headerData(self, section, orientation, role):
        header = ['Champion', 'Nick', 'Rank', '', '']

        if role == Qt.DisplayRole:
            return header[section]


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.stackedWidget.setCurrentIndex(1)

        self.model = TeamModel(self.ourTeamTable)
        self.ourTeamTable.setModel(self.model)
        self.ourTeamTable.verticalHeader().setVisible(False)
        self.ourTeamTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.threadpool = QThreadPool()

        self.lcu = LCU()
        self.lcu.signals.result.connect(self.handle_msg)
        self.threadpool.start(self.lcu)

    def handle_msg(self, msg):
        print(msg)

        msgType = msg[0]

        if msgType == Messages.LCU_CONNECTED:
            self.waitingLabel.setText('Waiting for champion select')
        elif msgType == Messages.LCU_DISCONNECTED:
            self.waitingLabel.setText('Waiting for league client')
        elif msgType == Messages.ENTERED_CHAMPSELECT:
            self.stackedWidget.setCurrentIndex(1)
        elif msgType == Messages.QUIT_CHAMPSELECT:
            self.stackedWidget.setCurrentIndex(0)
        elif msgType == Messages.CHAMPSELECT_UPDATED:
            summ = msg[1]
            self.model.setData(summ.lobbyPos, summ)
            self.model.layoutChanged.emit()


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
