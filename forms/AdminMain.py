# Form implementation generated from reading ui file 'ui/AdminMain.ui'
#
# Created by: PyQt6 UI code generator 6.8.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_AdminMainWindow(object):
    def setupUi(self, AdminMainWindow):
        AdminMainWindow.setObjectName("AdminMainWindow")
        AdminMainWindow.resize(1037, 815)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("ui\\../images/csuLogo.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        AdminMainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(parent=AdminMainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.frameInfo = QtWidgets.QFrame(parent=self.centralwidget)
        self.frameInfo.setEnabled(True)
        self.frameInfo.setGeometry(QtCore.QRect(40, 80, 371, 491))
        self.frameInfo.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frameInfo.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frameInfo.setObjectName("frameInfo")
        self.first_nameLabel = QtWidgets.QLabel(parent=self.frameInfo)
        self.first_nameLabel.setGeometry(QtCore.QRect(20, 90, 71, 16))
        self.first_nameLabel.setObjectName("first_nameLabel")
        self.rfidLabel = QtWidgets.QLabel(parent=self.frameInfo)
        self.rfidLabel.setGeometry(QtCore.QRect(20, 40, 71, 16))
        self.rfidLabel.setObjectName("rfidLabel")
        self.plateLabel = QtWidgets.QLabel(parent=self.frameInfo)
        self.plateLabel.setGeometry(QtCore.QRect(20, 200, 55, 16))
        self.plateLabel.setObjectName("plateLabel")
        self.plateValue = QtWidgets.QLineEdit(parent=self.frameInfo)
        self.plateValue.setGeometry(QtCore.QRect(100, 200, 181, 31))
        self.plateValue.setObjectName("plateValue")
        self.first_nameValue = QtWidgets.QLineEdit(parent=self.frameInfo)
        self.first_nameValue.setGeometry(QtCore.QRect(100, 90, 181, 31))
        self.first_nameValue.setObjectName("first_nameValue")
        self.nameValue_2 = QtWidgets.QLineEdit(parent=self.frameInfo)
        self.nameValue_2.setGeometry(QtCore.QRect(100, 40, 181, 31))
        self.nameValue_2.setObjectName("nameValue_2")
        self.registerLabel = QtWidgets.QLabel(parent=self.frameInfo)
        self.registerLabel.setGeometry(QtCore.QRect(130, 10, 81, 16))
        self.registerLabel.setObjectName("registerLabel")
        self.last_nameValue = QtWidgets.QLineEdit(parent=self.frameInfo)
        self.last_nameValue.setGeometry(QtCore.QRect(100, 140, 181, 31))
        self.last_nameValue.setObjectName("last_nameValue")
        self.last_nameLabel = QtWidgets.QLabel(parent=self.frameInfo)
        self.last_nameLabel.setGeometry(QtCore.QRect(20, 140, 71, 16))
        self.last_nameLabel.setObjectName("last_nameLabel")
        self.driver_typeLabel = QtWidgets.QLabel(parent=self.frameInfo)
        self.driver_typeLabel.setGeometry(QtCore.QRect(20, 250, 71, 16))
        self.driver_typeLabel.setObjectName("driver_typeLabel")
        self.driver_typeValue = QtWidgets.QLineEdit(parent=self.frameInfo)
        self.driver_typeValue.setGeometry(QtCore.QRect(100, 250, 181, 31))
        self.driver_typeValue.setObjectName("driver_typeValue")
        self.licenseLabel = QtWidgets.QLabel(parent=self.frameInfo)
        self.licenseLabel.setGeometry(QtCore.QRect(20, 300, 71, 16))
        self.licenseLabel.setObjectName("licenseLabel")
        self.licenseValue = QtWidgets.QLineEdit(parent=self.frameInfo)
        self.licenseValue.setGeometry(QtCore.QRect(100, 300, 181, 31))
        self.licenseValue.setObjectName("licenseValue")
        self.dateEdit = QtWidgets.QDateEdit(parent=self.frameInfo)
        self.dateEdit.setGeometry(QtCore.QRect(100, 350, 181, 31))
        self.dateEdit.setObjectName("dateEdit")
        self.licenseLabel_2 = QtWidgets.QLabel(parent=self.frameInfo)
        self.licenseLabel_2.setGeometry(QtCore.QRect(20, 350, 71, 16))
        self.licenseLabel_2.setObjectName("licenseLabel_2")
        self.licenseLabel_3 = QtWidgets.QLabel(parent=self.frameInfo)
        self.licenseLabel_3.setGeometry(QtCore.QRect(20, 400, 71, 16))
        self.licenseLabel_3.setObjectName("licenseLabel_3")
        self.dateEdit_2 = QtWidgets.QDateEdit(parent=self.frameInfo)
        self.dateEdit_2.setGeometry(QtCore.QRect(100, 400, 181, 31))
        self.dateEdit_2.setObjectName("dateEdit_2")
        self.licenseLabel_4 = QtWidgets.QLabel(parent=self.frameInfo)
        self.licenseLabel_4.setGeometry(QtCore.QRect(20, 450, 81, 16))
        self.licenseLabel_4.setObjectName("licenseLabel_4")
        self.uploadButton = QtWidgets.QPushButton(parent=self.frameInfo)
        self.uploadButton.setGeometry(QtCore.QRect(100, 450, 181, 21))
        self.uploadButton.setObjectName("uploadButton")
        self.framePicture = QtWidgets.QFrame(parent=self.centralwidget)
        self.framePicture.setGeometry(QtCore.QRect(550, 80, 421, 321))
        self.framePicture.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.framePicture.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.framePicture.setObjectName("framePicture")
        self.userPhoto = QtWidgets.QLabel(parent=self.framePicture)
        self.userPhoto.setGeometry(QtCore.QRect(30, 20, 361, 271))
        self.userPhoto.setText("")
        self.userPhoto.setScaledContents(True)
        self.userPhoto.setObjectName("userPhoto")
        self.frameCSU = QtWidgets.QFrame(parent=self.centralwidget)
        self.frameCSU.setGeometry(QtCore.QRect(490, 500, 501, 181))
        self.frameCSU.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frameCSU.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frameCSU.setObjectName("frameCSU")
        self.csuLabel = QtWidgets.QLabel(parent=self.frameCSU)
        self.csuLabel.setGeometry(QtCore.QRect(170, 140, 131, 31))
        font = QtGui.QFont()
        font.setFamily("MS Reference Sans Serif")
        font.setPointSize(12)
        self.csuLabel.setFont(font)
        self.csuLabel.setObjectName("csuLabel")
        self.buttonLogout = QtWidgets.QPushButton(parent=self.centralwidget)
        self.buttonLogout.setGeometry(QtCore.QRect(520, 710, 351, 28))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.buttonLogout.setFont(font)
        self.buttonLogout.setAutoFillBackground(False)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("ui\\../images/logoutIcon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.buttonLogout.setIcon(icon1)
        self.buttonLogout.setObjectName("buttonLogout")
        self.csuLogo = QtWidgets.QLabel(parent=self.centralwidget)
        self.csuLogo.setGeometry(QtCore.QRect(660, 510, 121, 121))
        self.csuLogo.setLineWidth(0)
        self.csuLogo.setText("")
        self.csuLogo.setPixmap(QtGui.QPixmap("ui\\../images/csuLogo.png"))
        self.csuLogo.setScaledContents(True)
        self.csuLogo.setObjectName("csuLogo")
        AdminMainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=AdminMainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1037, 26))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(parent=self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuExport_to = QtWidgets.QMenu(parent=self.menuFile)
        self.menuExport_to.setObjectName("menuExport_to")
        self.menuAbout = QtWidgets.QMenu(parent=self.menubar)
        self.menuAbout.setObjectName("menuAbout")
        AdminMainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=AdminMainWindow)
        self.statusbar.setObjectName("statusbar")
        AdminMainWindow.setStatusBar(self.statusbar)
        self.actionCSV = QtGui.QAction(parent=AdminMainWindow)
        self.actionCSV.setObjectName("actionCSV")
        self.action_xlsx = QtGui.QAction(parent=AdminMainWindow)
        self.action_xlsx.setObjectName("action_xlsx")
        self.action_txt = QtGui.QAction(parent=AdminMainWindow)
        self.action_txt.setObjectName("action_txt")
        self.actionExit = QtGui.QAction(parent=AdminMainWindow)
        self.actionExit.setObjectName("actionExit")
        self.menuExport_to.addAction(self.actionCSV)
        self.menuExport_to.addAction(self.action_xlsx)
        self.menuExport_to.addAction(self.action_txt)
        self.menuFile.addAction(self.menuExport_to.menuAction())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())

        self.retranslateUi(AdminMainWindow)
        QtCore.QMetaObject.connectSlotsByName(AdminMainWindow)

    def retranslateUi(self, AdminMainWindow):
        _translate = QtCore.QCoreApplication.translate
        AdminMainWindow.setWindowTitle(_translate("AdminMainWindow", "CSU-VecMon"))
        self.first_nameLabel.setText(_translate("AdminMainWindow", "First Name:"))
        self.rfidLabel.setText(_translate("AdminMainWindow", "Driver Code:"))
        self.plateLabel.setText(_translate("AdminMainWindow", "Plate No:"))
        self.registerLabel.setText(_translate("AdminMainWindow", "Driver Details"))
        self.last_nameLabel.setText(_translate("AdminMainWindow", "Last Name:"))
        self.driver_typeLabel.setText(_translate("AdminMainWindow", "Driver Type:"))
        self.licenseLabel.setText(_translate("AdminMainWindow", "License No.:"))
        self.licenseLabel_2.setText(_translate("AdminMainWindow", "CR Expiry:"))
        self.licenseLabel_3.setText(_translate("AdminMainWindow", "OR Expiry:"))
        self.licenseLabel_4.setText(_translate("AdminMainWindow", "Driver Photo:"))
        self.uploadButton.setText(_translate("AdminMainWindow", "Upload Photo"))
        self.csuLabel.setText(_translate("AdminMainWindow", "CSU VecMon"))
        self.buttonLogout.setText(_translate("AdminMainWindow", "LOGOUT"))
        self.menuFile.setTitle(_translate("AdminMainWindow", "File"))
        self.menuExport_to.setTitle(_translate("AdminMainWindow", "Export to"))
        self.menuAbout.setTitle(_translate("AdminMainWindow", "About"))
        self.actionCSV.setText(_translate("AdminMainWindow", ".csv"))
        self.action_xlsx.setText(_translate("AdminMainWindow", ".xlsx"))
        self.action_txt.setText(_translate("AdminMainWindow", ".txt"))
        self.actionExit.setText(_translate("AdminMainWindow", "Exit"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    AdminMainWindow = QtWidgets.QMainWindow()
    ui = Ui_AdminMainWindow()
    ui.setupUi(AdminMainWindow)
    AdminMainWindow.show()
    sys.exit(app.exec())
