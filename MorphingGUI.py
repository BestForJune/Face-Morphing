# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MorphingGUI.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1018, 878)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.btnStart = QtWidgets.QPushButton(self.centralwidget)
        self.btnStart.setGeometry(QtCore.QRect(20, 10, 151, 27))
        self.btnStart.setObjectName("btnStart")
        self.btnEnd = QtWidgets.QPushButton(self.centralwidget)
        self.btnEnd.setGeometry(QtCore.QRect(520, 10, 141, 27))
        self.btnEnd.setObjectName("btnEnd")
        self.graEnd = QtWidgets.QGraphicsView(self.centralwidget)
        self.graEnd.setGeometry(QtCore.QRect(520, 50, 480, 360))
        self.graEnd.setObjectName("graEnd")
        self.lblStart = QtWidgets.QLabel(self.centralwidget)
        self.lblStart.setGeometry(QtCore.QRect(180, 420, 111, 17))
        self.lblStart.setObjectName("lblStart")
        self.lblEnd = QtWidgets.QLabel(self.centralwidget)
        self.lblEnd.setGeometry(QtCore.QRect(730, 420, 101, 17))
        self.lblEnd.setObjectName("lblEnd")
        self.chkTriangle = QtWidgets.QCheckBox(self.centralwidget)
        self.chkTriangle.setGeometry(QtCore.QRect(440, 420, 131, 22))
        self.chkTriangle.setObjectName("chkTriangle")
        self.sliAlpha = QtWidgets.QSlider(self.centralwidget)
        self.sliAlpha.setGeometry(QtCore.QRect(130, 460, 751, 20))
        self.sliAlpha.setMaximum(20)
        self.sliAlpha.setSingleStep(1)
        self.sliAlpha.setOrientation(QtCore.Qt.Horizontal)
        self.sliAlpha.setObjectName("sliAlpha")
        self.lblAlpha = QtWidgets.QLabel(self.centralwidget)
        self.lblAlpha.setGeometry(QtCore.QRect(60, 460, 41, 17))
        self.lblAlpha.setObjectName("lblAlpha")
        self.txtAlpha = QtWidgets.QLineEdit(self.centralwidget)
        self.txtAlpha.setGeometry(QtCore.QRect(910, 460, 51, 27))
        self.txtAlpha.setObjectName("txtAlpha")
        self.lbl00 = QtWidgets.QLabel(self.centralwidget)
        self.lbl00.setGeometry(QtCore.QRect(130, 490, 62, 17))
        self.lbl00.setObjectName("lbl00")
        self.lbl10 = QtWidgets.QLabel(self.centralwidget)
        self.lbl10.setGeometry(QtCore.QRect(860, 490, 31, 17))
        self.lbl10.setObjectName("lbl10")
        self.graBlend = QtWidgets.QGraphicsView(self.centralwidget)
        self.graBlend.setGeometry(QtCore.QRect(220, 490, 480, 360))
        self.graBlend.setObjectName("graBlend")
        self.lblBlend = QtWidgets.QLabel(self.centralwidget)
        self.lblBlend.setGeometry(QtCore.QRect(720, 540, 121, 17))
        self.lblBlend.setObjectName("lblBlend")
        self.btnBlend = QtWidgets.QPushButton(self.centralwidget)
        self.btnBlend.setGeometry(QtCore.QRect(730, 570, 92, 27))
        self.btnBlend.setObjectName("btnBlend")
        self.graStart = QtWidgets.QGraphicsView(self.centralwidget)
        self.graStart.setGeometry(QtCore.QRect(20, 50, 480, 360))
        self.graStart.setObjectName("graStart")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btnStart.setText(_translate("MainWindow", "Load Starting Image"))
        self.btnEnd.setText(_translate("MainWindow", "Load Ending Image"))
        self.lblStart.setText(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Starting Image</span></p></body></html>"))
        self.lblEnd.setText(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Ending Image</span></p></body></html>"))
        self.chkTriangle.setText(_translate("MainWindow", "Show Triangles"))
        self.lblAlpha.setText(_translate("MainWindow", "Alpha"))
        self.lbl00.setText(_translate("MainWindow", "0.0"))
        self.lbl10.setText(_translate("MainWindow", "1.0"))
        self.lblBlend.setText(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Blending Result</span></p></body></html>"))
        self.btnBlend.setText(_translate("MainWindow", "Blend"))

