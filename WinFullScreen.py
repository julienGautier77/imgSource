#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  8 14:46:20 2019
Windows for plot
@author: juliengautier
"""

import pyqtgraph as pg # pyqtgraph biblio permettent l'affichage 

import qdarkstyle # pip install qdakstyle https://github.com/ColinDuquesnoy/QDarkStyleSheet  sur conda
from PyQt5.QtWidgets import QApplication,QHBoxLayout,QWidget,QCheckBox,QLabel,QVBoxLayout,QPushButton,QMessageBox,QSizePolicy
from pyqtgraph.Qt import QtCore,QtGui
import sys,time
import numpy as np
import pathlib,os
from PyQt5.QtGui import QIcon



class FULLSCREEN(QWidget):
    
    def __init__(self,title='Full Screen',conf=None,nbcam='cam1'):
        super(FULLSCREEN, self).__init__()
        
        p = pathlib.Path(__file__)
        sepa=os.sep
        self.nbcam=nbcam
        self.title=title
        self.icon=str(p.parent) + sepa+'icons' +sepa
        
        self.isWinOpen=False
        
        
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.icon+'LOA.png'))
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.vLine = pg.InfiniteLine(angle=90, movable=False,pen='y')
        self.hLine = pg.InfiniteLine(angle=0, movable=False,pen='y')
        self.cutData=[]
        
        self.bloqq=1
        if conf==None:
            self.confCCD=QtCore.QSettings(str(p.parent / 'confImgSource.ini'), QtCore.QSettings.IniFormat)
        else :
            self.confCCD=conf
        
        self.setup()
       
       
    def setup(self):
        
        
    
        self.winImage = pg.GraphicsLayoutWidget()
        self.winImage.setContentsMargins(0,0,0,0)
        self.winImage.setAspectLocked(True)
        self.winImage.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.winImage.ci.setContentsMargins(0,0,0,0)
        
        vbox2=QVBoxLayout()
        vbox2.addWidget(self.winImage)
        vbox2.setContentsMargins(1,1,1,1)
        
    
        self.p1=self.winImage.addPlot()
        self.imh=pg.ImageItem()
        self.p1.addItem(self.imh)
        self.p1.setMouseEnabled(x=False,y=False)
        self.p1.setContentsMargins(0,0,0,0)
        self.p1.setAspectLocked(True,ratio=1)
        self.p1.showAxis('right',show=False)
        self.p1.showAxis('top',show=False)
        self.p1.showAxis('left',show=False)
        self.p1.showAxis('bottom',show=False)
        
        self.vLine = pg.InfiniteLine(angle=90, movable=False,pen='y')
        self.hLine = pg.InfiniteLine(angle=0, movable=False,pen='y')
        self.p1.addItem(self.vLine)
        self.p1.addItem(self.hLine, ignoreBounds=False)
        self.xc=int(self.confCCD.value(self.nbcam+"/xc"))
        self.yc=int(self.confCCD.value(self.nbcam+"/yc"))
        self.rx=int(self.confCCD.value(self.nbcam+"/rx"))
        self.ry=int(self.confCCD.value(self.nbcam+"/ry"))
        self.vLine.setPos(self.xc)
        self.hLine.setPos(self.yc)
        
        self.ro1=pg.EllipseROI([self.xc,self.yc],[self.rx,self.ry],pen='y',movable=False,maxBounds=QtCore.QRectF(0,0,self.rx,self.ry))
        self.ro1.setPos([self.xc-(self.rx/2),self.yc-(self.ry/2)])
        self.p1.addItem(self.ro1)
        
        self.hist = pg.HistogramLUTItem() 
        self.hist.setImageItem(self.imh)
        self.hist.autoHistogramRange()
        self.hist.gradient.loadPreset('flame')
        HLayout=QHBoxLayout()
    
        HLayout.addLayout(vbox2)
        self.setLayout(HLayout)
        
        
        
    def Display(self,data,autoLevels=True,color='flame'):  
        self.imh.setImage(data.astype(float),autoLevels=autoLevels,autoDownsample=True)
        self.hist.gradient.loadPreset(color)
        
    def SetTITLE(self,title):
        self.setWindowTitle(title)
        
    def showFullScree(self):
        self.showMaximized()  
        
    def closeEvent(self, event):
        """ when closing the window
        """
        self.isWinOpen=False
        time.sleep(0.1)
        event.accept()
    
        
    
if __name__ == "__main__":
    appli = QApplication(sys.argv) 
    appli.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    e = FULLSCREEN() 
    e.show()
    appli.exec_()     
        
