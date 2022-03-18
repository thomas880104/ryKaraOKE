# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QFileDialog
from PyQt5.QtWidgets import QPushButton,QGraphicsColorizeEffect
from PyQt5.QtCore import QSize,QRect,QEventLoop
from mytubespleeter import Downloading_music,myspleeterrun
import sys
import os

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        
        self.allo = False
        self.NoNet = False
        
        self.setMinimumSize(QSize(465, 336))   
        self.setMaximumSize(QSize(465, 336))
        self.setWindowTitle("YoutubeKaraOKE") 

        self.nameLabel = QLabel(self)
        self.nameLabel.setText('請輸入想下載的音樂連結:')
        self.nameLabel.setGeometry(QRect(60, 90, 350, 41))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.nameLabel.setFont(font)
        
        self.TextLabel = QLabel(self)
        
        self.TextLabel.setGeometry(QRect(120, 230, 350, 41))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(12)
        self.TextLabel.setFont(font)
        
        
        self.inputlineEdit = QLineEdit(self)
        self.inputlineEdit.setGeometry(QRect(82, 150, 291, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.inputlineEdit.setFont(font)
        self.inputlineEdit.setObjectName("inputlineEdit")

        pybutton = QPushButton('onvocal', self)
        pybutton.clicked.connect(self.onvocal)
        pybutton.setGeometry(QRect(110, 200, 75, 23))
        pybutton.setObjectName("inputcheck")

        pybutton = QPushButton('offvocal', self)
        pybutton.clicked.connect(self.offvocal)
        pybutton.setGeometry(QRect(190, 200, 75, 23))
        pybutton.setObjectName("inputcheck")
        
        pybutton = QPushButton('本地檔案', self)
        pybutton.clicked.connect(self.localfile)
        pybutton.setGeometry(QRect(270, 200, 75, 23))
        pybutton.setObjectName("inputcheck")
        
        
    def undetectedURL(self):
        self.TextLabel.setStyleSheet("color: red;")
        self.TextLabel.setText('這個連結是無效的，請重新輸入')

    def onvocal(self):
        URL = self.inputlineEdit.text()
        self.TextLabel.setStyleSheet("color: black;")
        self.TextLabel.setText('請稍等...')
        try:
            
            song_name = Downloading_music(URL)
            myspleeterrun(song_name,mode = 'onvocal')
            self.allo = True
            self.close()
        except Exception as e:
            print(e.args)
            self.undetectedURL()

    def offvocal(self):
        URL = self.inputlineEdit.text()
        self.TextLabel.setStyleSheet("color: black;")
        self.TextLabel.setText('請稍等...')
        try:
            song_name = Downloading_music(URL)
            myspleeterrun(song_name)
            self.allo = True
            self.close()
        except Exception as e:
            print(e.args)
            self.undetectedURL()
    def localfile(self):
        self.filename, _= QFileDialog.getOpenFileName(self, 'Open file', './NoNetSongs',"Songs (*.wav)")
        self.NoNet = True
        self.allo = True
        self.close()



if __name__=='__main__': 
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())

    
