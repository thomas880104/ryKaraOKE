# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QFileDialog, QCheckBox, QApplication
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QSize,QRect,QCoreApplication
from mytubespleeter import Downloading_music,myspleeterrun,localfile_spleeter
import sys
import os

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        
        self.allo = False
        self.NoNet = False
        self.video = None
        
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
        
        self.checkbox = QCheckBox('背景播放影片', self)
        self.checkbox.setGeometry(190, 260, 100, 23)

        
    def undetectedURL(self, error_code):
        self.TextLabel.setStyleSheet("color: red;")
        self.TextLabel.setText(str(error_code))

    def onvocal(self):
        URL = self.inputlineEdit.text()
        self.TextLabel.setStyleSheet("color: black;")
        self.TextLabel.setText('請稍等...')
        self.video = self.checkbox.isChecked()
        try:
            self.mode = 'onvocal'
            song_name = Downloading_music(URL,self.video)
            myspleeterrun(song_name,mode = 'onvocal')
            self.allo = True
            self.filename = song_name
            self.close()
        except Exception as e:
            print(e.args)
            self.undetectedURL(error_code = e.args)

    def offvocal(self):
        URL = self.inputlineEdit.text()
        self.TextLabel.setStyleSheet("color: black;")
        self.TextLabel.setText('請稍等...')
        self.video = self.checkbox.isChecked()
        try:
            self.mode = 'offvocal'
            song_name = Downloading_music(URL,self.video)
            myspleeterrun(song_name)
            self.filename = song_name
            self.allo = True
            self.close()
        except Exception as e:
            print(e.args)
            self.undetectedURL(error_code = e.args)
    def localfile(self):
        self.filename, _= QFileDialog.getOpenFileName(self, 'Open file', './localfile',"Songs (*.wav *.mp4)")
        self.NoNet = True

        self.mode = 'onvocal'
        if self.filename[-3:] == 'mp4':
            self.video = True
            self.filename = localfile_spleeter(self.filename)
            self.NoNet = False

        '''
        elif self.filename[-3:] == 'wav':
            myspleeterrun(self.filename)
        '''
        self.allo = True
        self.close()



if __name__=='__main__': 
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())

    
