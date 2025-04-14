# Form implementation generated from reading ui file 'ui/Main.ui'
#
# Created by: PyQt6 UI code generator 6.8.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1104, 816)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("ui\\../images/csuLogo.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.mainGrid = QtWidgets.QGridLayout(self.centralwidget)
        self.mainGrid.setObjectName("mainGrid")
        self.headerLayout = QtWidgets.QHBoxLayout()
        self.headerLayout.setObjectName("headerLayout")
        self.csuLogo = QtWidgets.QLabel(parent=self.centralwidget)
        self.csuLogo.setMaximumSize(QtCore.QSize(120, 120))
        self.csuLogo.setPixmap(QtGui.QPixmap("ui\\../images/csuLogo.png"))
        self.csuLogo.setScaledContents(True)
        self.csuLogo.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading)
        self.csuLogo.setObjectName("csuLogo")
        self.headerLayout.addWidget(self.csuLogo)
        self.csuLabel = QtWidgets.QLabel(parent=self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("MS Reference Sans Serif")
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.csuLabel.setFont(font)
        self.csuLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.csuLabel.setObjectName("csuLabel")
        self.headerLayout.addWidget(self.csuLabel)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.headerLayout.addItem(spacerItem)
        self.mainGrid.addLayout(self.headerLayout, 0, 0, 1, 2)
        self.leftLayout = QtWidgets.QVBoxLayout()
        self.leftLayout.setObjectName("leftLayout")
        self.userPhoto = QtWidgets.QLabel(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.userPhoto.sizePolicy().hasHeightForWidth())
        self.userPhoto.setSizePolicy(sizePolicy)
        self.userPhoto.setMinimumSize(QtCore.QSize(300, 300))
        self.userPhoto.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.userPhoto.setText("")
        self.userPhoto.setScaledContents(True)
        self.userPhoto.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.userPhoto.setObjectName("userPhoto")
        self.leftLayout.addWidget(self.userPhoto)
        self.detailsForm = QtWidgets.QFormLayout()
        self.detailsForm.setObjectName("detailsForm")
        self.rfidLabel = QtWidgets.QLabel(parent=self.centralwidget)
        self.rfidLabel.setObjectName("rfidLabel")
        self.detailsForm.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.rfidLabel)
        self.rfidValue = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.rfidValue.setReadOnly(True)
        self.rfidValue.setObjectName("rfidValue")
        self.detailsForm.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.rfidValue)
        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.detailsForm.setItem(1, QtWidgets.QFormLayout.ItemRole.LabelRole, spacerItem1)
        self.nameLabel = QtWidgets.QLabel(parent=self.centralwidget)
        self.nameLabel.setObjectName("nameLabel")
        self.detailsForm.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.nameLabel)
        self.nameValue = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.nameValue.setReadOnly(True)
        self.nameValue.setObjectName("nameValue")
        self.detailsForm.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.nameValue)
        spacerItem2 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.detailsForm.setItem(3, QtWidgets.QFormLayout.ItemRole.LabelRole, spacerItem2)
        self.plateLabel = QtWidgets.QLabel(parent=self.centralwidget)
        self.plateLabel.setObjectName("plateLabel")
        self.detailsForm.setWidget(4, QtWidgets.QFormLayout.ItemRole.LabelRole, self.plateLabel)
        self.plateValue = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.plateValue.setReadOnly(True)
        self.plateValue.setObjectName("plateValue")
        self.detailsForm.setWidget(4, QtWidgets.QFormLayout.ItemRole.FieldRole, self.plateValue)
        self.leftLayout.addLayout(self.detailsForm)
        self.mainGrid.addLayout(self.leftLayout, 1, 0, 1, 1)
        self.tableLogs = QtWidgets.QTableWidget(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.tableLogs.sizePolicy().hasHeightForWidth())
        self.tableLogs.setSizePolicy(sizePolicy)
        self.tableLogs.setMinimumSize(QtCore.QSize(400, 300))
        self.tableLogs.setShowGrid(True)
        self.tableLogs.setObjectName("tableLogs")
        self.tableLogs.setColumnCount(5)
        self.tableLogs.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableLogs.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableLogs.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableLogs.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableLogs.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableLogs.setHorizontalHeaderItem(4, item)
        self.tableLogs.horizontalHeader().setStretchLastSection(True)
        self.mainGrid.addWidget(self.tableLogs, 1, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1104, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(parent=self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuAbout = QtWidgets.QMenu(parent=self.menubar)
        self.menuAbout.setObjectName("menuAbout")
        self.menuOptions = QtWidgets.QMenu(parent=self.menubar)
        self.menuOptions.setObjectName("menuOptions")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionCSV = QtGui.QAction(parent=MainWindow)
        self.actionCSV.setObjectName("actionCSV")
        self.action_xlsx = QtGui.QAction(parent=MainWindow)
        self.action_xlsx.setObjectName("action_xlsx")
        self.action_txt = QtGui.QAction(parent=MainWindow)
        self.action_txt.setObjectName("action_txt")
        self.actionExit = QtGui.QAction(parent=MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("ui\\../../../../../Downloads/Compressed/fugue-icons-3.5.6-src/icons/door-open-out.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionExit.setIcon(icon1)
        self.actionExit.setObjectName("actionExit")
        self.actionAbout = QtGui.QAction(parent=MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("ui\\../../../../../Downloads/Compressed/fugue-icons-3.5.6-src/icons/question-button.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionAbout.setIcon(icon2)
        self.actionAbout.setObjectName("actionAbout")
        self.actionLogout = QtGui.QAction(parent=MainWindow)
        self.actionLogout.setIcon(icon1)
        self.actionLogout.setObjectName("actionLogout")
        self.menuAbout.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuOptions.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "CSU-VeMon"))
        self.csuLabel.setText(_translate("MainWindow", "CSU VeMon"))
        self.rfidLabel.setText(_translate("MainWindow", "RFID:"))
        self.nameLabel.setText(_translate("MainWindow", "Name:"))
        self.plateLabel.setText(_translate("MainWindow", "Plate No:"))
        item = self.tableLogs.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "RFID"))
        item = self.tableLogs.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Name"))
        item = self.tableLogs.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Plate No."))
        item = self.tableLogs.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Time"))
        item = self.tableLogs.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "Remarks"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuAbout.setTitle(_translate("MainWindow", "Help"))
        self.menuOptions.setTitle(_translate("MainWindow", "Options"))
        self.actionCSV.setText(_translate("MainWindow", ".csv"))
        self.action_xlsx.setText(_translate("MainWindow", ".xlsx"))
        self.action_txt.setText(_translate("MainWindow", ".txt"))
        self.actionExit.setText(_translate("MainWindow", "Logout"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionLogout.setText(_translate("MainWindow", "Logout"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
