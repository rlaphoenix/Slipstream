# pylint: disable-all
# type: ignore
# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.5.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize, Qt
from PySide6.QtGui import QAction, QFont, QIcon, QPixmap
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QFrame, QHBoxLayout, QLabel, QLayout, QMenu,
                               QMenuBar, QProgressBar, QPushButton, QScrollArea, QSizePolicy, QSpacerItem, QStatusBar,
                               QTreeWidget, QVBoxLayout, QWidget)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1000, 400)
        icon = QIcon()
        icon.addFile(u"static/img/music-disc-with-luster.svg", QSize(), QIcon.Normal, QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.cw = QWidget(MainWindow)
        self.cw.setObjectName(u"cw")
        self.verticalLayout_6 = QVBoxLayout(self.cw)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.deviceListFrame = QFrame(self.cw)
        self.deviceListFrame.setObjectName(u"deviceListFrame")
        self.deviceListFrame.setFrameShape(QFrame.Panel)
        self.deviceListFrame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.deviceListFrame)
        self.verticalLayout_2.setSpacing(16)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(20, 20, 20, 20)
        self.deviceListHeader = QHBoxLayout()
        self.deviceListHeader.setSpacing(16)
        self.deviceListHeader.setObjectName(u"deviceListHeader")
        self.deviceListHeader.setSizeConstraint(QLayout.SetMinimumSize)
        self.discIcon = QLabel(self.deviceListFrame)
        self.discIcon.setObjectName(u"discIcon")
        self.discIcon.setMinimumSize(QSize(20, 20))
        self.discIcon.setMaximumSize(QSize(20, 20))
        self.discIcon.setPixmap(QPixmap(u"static/img/music-disc-with-luster.svg"))
        self.discIcon.setScaledContents(True)

        self.deviceListHeader.addWidget(self.discIcon)

        self.deviceListL = QLabel(self.deviceListFrame)
        self.deviceListL.setObjectName(u"deviceListL")
        self.deviceListL.setMinimumSize(QSize(0, 28))
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(13)
        font.setBold(True)
        self.deviceListL.setFont(font)

        self.deviceListHeader.addWidget(self.deviceListL)

        self.refreshIcon = QPushButton(self.deviceListFrame)
        self.refreshIcon.setObjectName(u"refreshIcon")
        self.refreshIcon.setMaximumSize(QSize(36, 16777215))
        icon1 = QIcon()
        icon1.addFile(u"static/img/refresh.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.refreshIcon.setIcon(icon1)
        self.refreshIcon.setIconSize(QSize(20, 20))

        self.deviceListHeader.addWidget(self.refreshIcon)


        self.verticalLayout_2.addLayout(self.deviceListHeader)

        self.deviceListDevices = QScrollArea(self.deviceListFrame)
        self.deviceListDevices.setObjectName(u"deviceListDevices")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deviceListDevices.sizePolicy().hasHeightForWidth())
        self.deviceListDevices.setSizePolicy(sizePolicy)
        self.deviceListDevices.setMinimumSize(QSize(200, 0))
        self.deviceListDevices.setFrameShape(QFrame.NoFrame)
        self.deviceListDevices.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.deviceListDevices.setWidgetResizable(True)
        self.deviceListDevices_2 = QWidget()
        self.deviceListDevices_2.setObjectName(u"deviceListDevices_2")
        self.deviceListDevices_2.setGeometry(QRect(0, 0, 200, 200))
        self.verticalLayout_3 = QVBoxLayout(self.deviceListDevices_2)
        self.verticalLayout_3.setSpacing(16)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.exampleDevice = QPushButton(self.deviceListDevices_2)
        self.exampleDevice.setObjectName(u"exampleDevice")

        self.verticalLayout_3.addWidget(self.exampleDevice)

        self.deviceListSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.deviceListSpacer)

        self.deviceListDevices.setWidget(self.deviceListDevices_2)

        self.verticalLayout_2.addWidget(self.deviceListDevices)

        self.backupButton = QPushButton(self.deviceListFrame)
        self.backupButton.setObjectName(u"backupButton")
        font1 = QFont()
        font1.setFamilies([u"Calibri"])
        font1.setPointSize(12)
        font1.setBold(False)
        font1.setStyleStrategy(QFont.PreferDefault)
        self.backupButton.setFont(font1)

        self.verticalLayout_2.addWidget(self.backupButton)


        self.horizontalLayout.addWidget(self.deviceListFrame)

        self.discInfoFrame = QFrame(self.cw)
        self.discInfoFrame.setObjectName(u"discInfoFrame")
        self.discInfoFrame.setFrameShape(QFrame.Panel)
        self.discInfoFrame.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.discInfoFrame)
        self.verticalLayout.setSpacing(16)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)
        self.deviceInfoHeader = QHBoxLayout()
        self.deviceInfoHeader.setSpacing(16)
        self.deviceInfoHeader.setObjectName(u"deviceInfoHeader")
        self.deviceInfoHeader.setSizeConstraint(QLayout.SetMinimumSize)
        self.infoIcon = QLabel(self.discInfoFrame)
        self.infoIcon.setObjectName(u"infoIcon")
        self.infoIcon.setMinimumSize(QSize(20, 20))
        self.infoIcon.setMaximumSize(QSize(20, 20))
        self.infoIcon.setPixmap(QPixmap(u"static/img/info-circle.svg"))
        self.infoIcon.setScaledContents(True)

        self.deviceInfoHeader.addWidget(self.infoIcon)

        self.label_4 = QLabel(self.discInfoFrame)
        self.label_4.setObjectName(u"label_4")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy1)
        self.label_4.setMinimumSize(QSize(0, 28))
        self.label_4.setFont(font)

        self.deviceInfoHeader.addWidget(self.label_4)


        self.verticalLayout.addLayout(self.deviceInfoHeader)

        self.discInfoList = QTreeWidget(self.discInfoFrame)
        self.discInfoList.setObjectName(u"discInfoList")
        self.discInfoList.setFrameShape(QFrame.NoFrame)
        self.discInfoList.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.discInfoList.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.discInfoList.setColumnCount(2)
        self.discInfoList.header().setVisible(False)
        self.discInfoList.header().setCascadingSectionResizes(True)
        self.discInfoList.header().setMinimumSectionSize(175)
        self.discInfoList.header().setStretchLastSection(False)

        self.verticalLayout.addWidget(self.discInfoList)


        self.horizontalLayout.addWidget(self.discInfoFrame)


        self.verticalLayout_6.addLayout(self.horizontalLayout)

        self.progressBar = QProgressBar(self.cw)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(20)
        self.progressBar.setTextVisible(False)

        self.verticalLayout_6.addWidget(self.progressBar)

        MainWindow.setCentralWidget(self.cw)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1000, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuOpen_Recent = QMenu(self.menuFile)
        self.menuOpen_Recent.setObjectName(u"menuOpen_Recent")
        self.menuOpen_Recent.setEnabled(False)
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.menuOpen_Recent.menuAction())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Slipstream", None))
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"Open", None))
#if QT_CONFIG(shortcut)
        self.actionOpen.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
#if QT_CONFIG(shortcut)
        self.actionExit.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Q", None))
#endif // QT_CONFIG(shortcut)
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.deviceListL.setText(QCoreApplication.translate("MainWindow", u"Device list", None))
        self.exampleDevice.setText(QCoreApplication.translate("MainWindow", u"POKEMON\n"
"ASUS - SDRW-08U7M-U", None))
        self.backupButton.setText(QCoreApplication.translate("MainWindow", u"Backup", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Disc information", None))
        ___qtreewidgetitem = self.discInfoList.headerItem()
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("MainWindow", u"Value", None))
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MainWindow", u"Name", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuOpen_Recent.setTitle(QCoreApplication.translate("MainWindow", u"Open Recent", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi
