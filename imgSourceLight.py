# -*- coding: utf-8 -*-
"""
Created on Wed Nov  28 13:13:26 2018
Modified on Wed Dec 12 11:08:56 2018
Camera Imaging sources 
Gui for imangingsource camera use IC_ImagingControl 
PyQT5 and PyQtgraph
Pyhton 3.x
@author: LOA Julien Gautier
"""


from PyQt5.QtWidgets import QApplication,QVBoxLayout,QHBoxLayout,QWidget,QPushButton
from PyQt5.QtWidgets import QComboBox,QSlider,QCheckBox,QLabel,QSizePolicy
from pyqtgraph.Qt import QtCore,QtGui 
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QIcon

import sys
import pyqtgraph as pg # pyqtgraph biblio permettent l'affichage 
import numpy as np
try :
    import IC_ImagingControl 
except :
    pass



from WinFullScreen import FULLSCREEN
import qdarkstyle # pip install qdakstyle https://github.com/ColinDuquesnoy/QDarkStyleSheet  sur conda
import pathlib,os
from visu.winMeas import MEAS

class CameraAcqD(QWidget) :

    def __init__(self,name=None,visuGauche=False):
        super(CameraAcqD, self).__init__()
        self.visuGauche=visuGauche
        self.winM=MEAS()
        if name==None:
            self.nbcam='camTest'
        else:   
            self.nbcam=name
        self.confCCD = QtCore.QSettings('confCameras.ini', QtCore.QSettings.IniFormat)
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5()) # dark style 
        self.bloqHandle=1 # bloque la taille du cercle
        self.camType=self.confCCD.value(self.nbcam+"/camType")
        if self.camType != 'imgSource':
            print('error camera type')
        self.cameName=self.confCCD.value(self.nbcam+"/name")
        self.setWindowTitle(self.cameName)
        p = pathlib.Path(__file__)
        sepa=os.sep
        self.icon=str(p.parent) + sepa + 'icons' +sepa
        self.setWindowIcon(QIcon(self.icon+'LOA.png'))
        #pg.setConfigOptions(antialias=True)
        
        try :
            ic_ic = IC_ImagingControl.IC_ImagingControl()
            ic_ic.init_library()
        except :
            print('IC control Library not found')
            pass
        
        self.bloqq=1
        self.id=self.confCCD.value(self.nbcam+"/camId")
        self.camName=self.confCCD.value(self.nbcam+"/name")
        
        self.setup()
        self.Color()
        self.winSC=FULLSCREEN(title=self.cameName,conf=self.confCCD,nbcam=self.nbcam)
        self.actionButton()
        try :
            self.cam0= ic_ic.get_device((self.id.encode()))#cam_names[0])
            self.connected=1
            print(self.nbcam,"connected @",self.confCCD.value(self.nbcam+"/name"),'id:',self.id)
        except:
            self.connected=0
            print ('not connected')
            self.nbcam='camTest'
            self.runButton.setEnabled(False)
            self.runButton.setStyleSheet("background-color:gray")
            self.runButton.setStyleSheet("QPushButton:!pressed{image: url(./icons/Circled Play-595b40b65ba036ed117d436f.svg);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0,0)}""QPushButton:pressed{image: url(./icons/Circled Play-595b40b65ba036ed117d436f.svg);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0)}")
            
            self.hSliderShutter.setEnabled(False)
            self.trigg.setEnabled(False)
            self.hSliderGain.setEnabled(False)
            self.stopButton.setEnabled(False)
            self.stopButton.setStyleSheet("background-color:gray")
            self.stopButton.setStyleSheet("QPushButton:!pressed{border-image: url(./icons/Stop.svg);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0,0);}""QPushButton:pressed{image: url(./icons/Stop.svg);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0)}")

            
        if self.connected==1:
            self.cam0.open()
            #print(self.cam0.list_property_names())
            self.cam0.enable_continuous_mode(True)
            self.cam0.gain.auto=False
            self.cam0.exposure.auto=False
            self.cam0.set_frame_rate=float(25)
            frameRate=self.cam0.get_frame_rate()
            print('frame rate : ',frameRate)
            
            self.hSliderShutter.setMinimum(self.cam0.exposure.min)
            self.hSliderShutter.setMaximum(self.cam0.exposure.max)
            sh=int(self.confCCD.value(self.nbcam+"/shutter"))
            self.hSliderShutter.setValue(sh)
            self.cam0.exposure.value=int(sh)
            
            self.hSliderGain.setMinimum(self.cam0.gain.min)
            self.hSliderGain.setMaximum(self.cam0.gain.max)
            g=int(self.confCCD.value(self.nbcam+"/gain"))
            self.hSliderGain.setValue(g)
            self.cam0.gain.value=int(g)
            self.dimy=self.cam0.get_video_format_height()
            self.dimx=self.cam0.get_video_format_width()
            print("number of pixels :",self.dimx,'*',self.dimy)
            
        else :
            self.dimy=960
            self.dimx=1240
            
        
        def twoD_Gaussian(x,y, amplitude, xo, yo, sigma_x, sigma_y, theta, offset):
            xo = float(xo)
            yo = float(yo)    
            a = (np.cos(theta)**2)/(2*sigma_x**2) + (np.sin(theta)**2)/(2*sigma_y**2)
            b = -(np.sin(2*theta))/(4*sigma_x**2) + (np.sin(2*theta))/(4*sigma_y**2)
            c = (np.sin(theta)**2)/(2*sigma_x**2) + (np.cos(theta)**2)/(2*sigma_y**2)
            return offset + amplitude*np.exp( - (a*((x-xo)**2) + 2*b*(x-xo)*(y-yo) + c*((y-yo)**2)))

        # Create x and y indices
        x = np.arange(0,self.dimx)
        y = np.arange(0,self.dimy)
        y,x = np.meshgrid(y, x)

        self.data=twoD_Gaussian(x, y,250, 300, 600, 40, 40, 0, 10)+(50*np.random.rand(self.dimx,self.dimy)).round() 
        #self.data=(50*np.random.rand(self.dimx,self.dimy)).round() + 150
        
        self.p1.setXRange(0,self.dimx)
        self.p1.setYRange(0,self.dimy)
        #self.p1.setGeometry(1,1,self.dimx,self.dimy)
        #self.winImage.setGeometry(1,1,self.dimx,self.dimy)
        self.Display(self.data)
        
        
    def setup(self):    
        
        vbox1=QVBoxLayout() 
        
        
        self.camNameLabel=QLabel('nomcam',self)
        
        self.camNameLabel.setText(self.confCCD.value(self.nbcam+"/name"))

        self.camNameLabel.setAlignment(Qt.AlignCenter)
        self.camNameLabel.setStyleSheet('font: bold 20px')
        self.camNameLabel.setStyleSheet('color: yellow')
        vbox1.addWidget(self.camNameLabel)
        
        hbox1=QHBoxLayout() # horizontal layout pour run et stop
        self.runButton=QPushButton(self)
        self.runButton.setMaximumWidth(60)
        self.runButton.setMinimumHeight(60)
        self.runButton.setStyleSheet("QPushButton:!pressed{border-image: url(./icons/Circled Play-595b40b65ba036ed117d436f.svg);background-color: rgb(0, 0, 0,0) ;border-color: green;}""QPushButton:pressed{image: url(./icons/Circled Play-595b40b65ba036ed117d436f.svg);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0)}")
        self.stopButton=QPushButton(self)
        
        self.stopButton.setMaximumWidth(60)
        self.stopButton.setMinimumHeight(50)
        self.stopButton.setStyleSheet("QPushButton:!pressed{border-image: url(./icons/Stop.svg);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0,0);}""QPushButton:pressed{image: url(./icons/Stop.svg);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0)}")
        
        
        hbox1.addWidget(self.runButton)
        hbox1.addWidget(self.stopButton)
#        self.oneButton=QPushButton(self)
#        hbox1.addWidget(self.oneButton)
        
        vbox1.addLayout(hbox1)
        
        self.trigg=QComboBox()
        self.trigg.setMaximumWidth(60)
        self.trigg.addItem('OFF')
        self.trigg.addItem('ON')
        self.labelTrigger=QLabel('Trigger')
        self.labelTrigger.setMaximumWidth(60)
        self.itrig=self.trigg.currentIndex()
        hbox2=QHBoxLayout()
        hbox2.addWidget(self.labelTrigger)
        hbox2.addWidget(self.trigg)
        vbox1.addLayout(hbox2)
        
        self.labelExp=QLabel('Exposure')
        self.labelExp.setMaximumWidth(120)
        self.labelExp.setAlignment(Qt.AlignCenter)
        vbox1.addWidget(self.labelExp)
        self.hSliderShutter=QSlider(Qt.Horizontal)
       
        self.hSliderShutter.setMaximumWidth(120)
        vbox1.addWidget(self.hSliderShutter)
        
        self.labelGain=QLabel('Gain')
        self.labelGain.setMaximumWidth(120)
        self.labelGain.setAlignment(Qt.AlignCenter)
        vbox1.addWidget(self.labelGain)
        self.hSliderGain=QSlider(Qt.Horizontal)
        self.hSliderGain.setMaximumWidth(120)
        vbox1.addWidget(self.hSliderGain)
        
        hbox3=QHBoxLayout()
        self.checkBoxScale=QCheckBox('AScale',self)
        self.checkBoxScale.setChecked(True)
        self.checkBoxScale.setStyleSheet("QCheckBox::indicator{width: 30px;height: 30px;}""QCheckBox::indicator:unchecked { image : url(./icons/Toggle Off-595b40b85ba036ed117dac78.svg);}""QCheckBox::indicator:checked { image:  url(./icons/Toggle On-595b40b85ba036ed117dac79.svg);}")
    
        hbox3.addWidget(self.checkBoxScale)
        
        self.checkBoxColor=QCheckBox('Color',self)
        self.checkBoxColor.setChecked(True)
        self.checkBoxColor.setStyleSheet("QCheckBox::indicator{width: 30px;height: 30px;}""QCheckBox::indicator:unchecked { image : url(./icons/Toggle Off-595b40b85ba036ed117dac78.svg);}""QCheckBox::indicator:checked { image:  url(./icons/Toggle On-595b40b85ba036ed117dac79.svg);}")
    
        hbox3.addWidget(self.checkBoxColor)
        
        vbox1.addLayout(hbox3)
        hbox4=QHBoxLayout()
        self.checkBoxZoom=QCheckBox('Zoom',self)
        self.checkBoxZoom.setChecked(False)
        self.checkBoxZoom.setStyleSheet("QCheckBox::indicator{width: 30px;height: 30px;}""QCheckBox::indicator:unchecked { image : url(./icons/Toggle Off-595b40b85ba036ed117dac78.svg);}""QCheckBox::indicator:checked { image:  url(./icons/Toggle On-595b40b85ba036ed117dac79.svg);}")
    
        hbox4.addWidget(self.checkBoxZoom)
        
        self.MeasButton=QCheckBox('Meas',self)
        self.MeasButton.setChecked(False)
        self.MeasButton.setStyleSheet("QCheckBox::indicator{width: 30px;height: 30px;}""QCheckBox::indicator:unchecked { image : url(./icons/Toggle Off-595b40b85ba036ed117dac78.svg);}""QCheckBox::indicator:checked { image:  url(./icons/Toggle On-595b40b85ba036ed117dac79.svg);}")
    
        hbox4.addWidget(self.MeasButton)
        
        
        vbox1.addLayout(hbox4)
        
        vbox1.setContentsMargins(0,0,0,0)
        vbox1.addStretch(1)
        self.vbox1=vbox1
        
        ### affichage image###
        
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
        
        self.ro1=pg.EllipseROI([self.xc,self.yc],[self.rx,self.ry],pen='y',movable=False)#maxBounds=QtCore.QRectF(0,0,self.rx,self.ry)
        self.ro1.setPos([self.xc-(self.rx/2),self.yc-(self.ry/2)])
        self.p1.addItem(self.ro1)
        
        
        #histogramme
        self.hist = pg.HistogramLUTItem() 
        self.hist.setImageItem(self.imh)
        self.hist.autoHistogramRange()
        self.hist.gradient.loadPreset('flame')
        
        ## Graph coupe XY  
        
        self.curve2=pg.PlotCurveItem()
        self.curve3=pg.PlotCurveItem()
        
        ## main layout
        
        hMainLayout=QHBoxLayout()
        if self.visuGauche==True:
            hMainLayout.addLayout(self.vbox1)
            hMainLayout.addLayout(vbox2)
        else:
            hMainLayout.addLayout(vbox2)
            hMainLayout.addLayout(self.vbox1)
        hMainLayout.setContentsMargins(1,1,1,1)
        hMainLayout.setSpacing(1)
        hMainLayout.setStretch(3,1)
        
        self.setLayout(hMainLayout)
        self.setContentsMargins(1,1,1,1)
        
        # Blocage de la souris
        self.shortcutb=QtGui.QShortcut(QtGui.QKeySequence("Ctrl+b"),self)
        self.shortcutb.activated.connect(self.bloquer)
        self.shortcutb.setContext(Qt.ShortcutContext(3))
        self.shortcutd=QtGui.QShortcut(QtGui.QKeySequence("Ctrl+d"),self)
        self.shortcutd.activated.connect(self.debloquer)
        self.shortcutd.setContext(Qt.ShortcutContext(3))
        self.shortcutPu=QShortcut(QtGui.QKeySequence("+"),self)
        self.shortcutPu.activated.connect(self.paletteup)
        self.shortcutPu.setContext(Qt.ShortcutContext(3))
        #3: The shortcut is active when its parent widget, or any of its children has focus. default O The shortcut is active when its parent widget has focus.
        self.shortcutPd=QtGui.QShortcut(QtGui.QKeySequence("-"),self)
        self.shortcutPd.activated.connect(self.palettedown)
        self.shortcutPd.setContext(Qt.ShortcutContext(3))
        
        # mvt de la souris
        self.proxy=pg.SignalProxy(self.p1.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.vb=self.p1.vb
        
        # text pour afficher fwhm sur p1
        self.textX = pg.TextItem(angle=-90) 
        self.textY = pg.TextItem()
        
        
    def actionButton(self):
        self.runButton.clicked.connect(self.acquireMultiImage)
        self.stopButton.clicked.connect(self.stopAcq)
        self.hSliderShutter.sliderMoved.connect(self.Shutter)
        self.hSliderGain.sliderMoved.connect(self.Gain)
        self.trigg.currentIndexChanged.connect(self.Trig)
        self.checkBoxColor.stateChanged.connect(self.Color)
        
        self.ro1.sigRegionChangeFinished.connect(self.roiChanged)
        self.checkBoxZoom.stateChanged.connect(self.Zoom)
        self.MeasButton.clicked.connect(self.Measurement)
#        self.oneButton.clicked.connect(self.acquireOneImage)
        
    def Shutter(self):
        sh=self.hSliderShutter.value()
        self.cam0.exposure.auto=False
        self.cam0.exposure.value=int(sh)
#        print(self.cam0.exposure.value,'sh:',sh)
        self.confCCD.setValue(self.nbcam+"/shutter",int(sh))
        
    
    def Color(self):
        """ image in colour
        """
        if self.checkBoxColor.isChecked()==1:
            self.color='flame'
            self.hist.gradient.loadPreset('flame')
        else:
            self.hist.gradient.loadPreset('grey')
            self.color='grey'
            
    def Zoom(self):
        if self.checkBoxZoom.isChecked()==1:
            self.p1.setXRange(self.xc-200,self.xc+200)
            self.p1.setYRange(self.yc-200,self.yc+200)
        else:
            self.p1.setXRange(0,self.dimx)
            self.p1.setYRange(0,self.dimy)
        
    
         
    def Gain(self):
        g=self.hSliderGain.value()
        self.cam0.gain.value=int(g)
        self.confCCD.setValue(self.nbcam+"/gain",int(g))
#        print("gain:",self.cam0.gain.value)
        
    def Trig(self):
        self.itrig=self.trigg.currentIndex()
        
        if self.itrig==0:
            self.cam0.enable.trigger(False)
#            print ("trigger OFF")
        if self.itrig==1:
            self.cam0.enable_trigger(True)
#            print("Trigger ON")
        
    def acquireMultiImage(self):   
        #print('live...')
        
        self.runButton.setEnabled(False)
        self.runButton.setStyleSheet("QPushButton:!pressed{border-image: url(./icons/Circled Play-595b40b65ba036ed117d436f.svg);background-color: gray ;border-color: rgb(0, 0, 0,0);}""QPushButton:pressed{image: url(./icons/Circled Play-595b40b65ba036ed117d436f.svg);background-color: gray ;border-color: rgb(0, 0, 0)}")
        #self.runButton.setStyleSheet("background-color:gray")
        try:
            self.threadRunAcq=ThreadRunAcq(self)
            self.threadRunAcq.newDataRun.connect(self.Display)
            self.threadRunAcq.start()
        except :
            pass
    
    
    def acquireOneImage(self):   
        
        
        self.runButton.setEnabled(False)
        self.runButton.setStyleSheet("QPushButton:!pressed{border-image: url(./icons/Circled Play-595b40b65ba036ed117d436f.svg);background-color: gray ;border-color: rgb(0, 0, 0,0);}""QPushButton:pressed{image: url(./icons/Circled Play-595b40b65ba036ed117d436f.svg);background-color: gray ;border-color: rgb(0, 0, 0)}")
        #self.runButton.setStyleSheet("background-color:gray")
        try:
            self.threadOneAcq=ThreadOneAcq(self)
            self.threadOneAcq.newDataOne.connect(self.Display)
            self.threadOneAcq.start()
        except :
            print('error')
            pass
        self.runButton.setEnabled(True)
        self.runButton.setStyleSheet("QPushButton:!pressed{border-image: url(./icons/Circled Play-595b40b65ba036ed117d436f.svg);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0,0);}""QPushButton:pressed{image: url(./icons/Circled Play-595b40b65ba036ed117d436f.svg);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0)}")
        
    
    
    def stopAcq(self):
#        print('Stop live')
        try:
            self.threadRunAcq.stopThreadRunAcq()
        except :
            pass
        self.runButton.setEnabled(True)
        #self.runButton.setStyleSheet("background-color: rgb(0, 200, 0)")
        self.runButton.setStyleSheet("QPushButton:!pressed{border-image: url(./icons/Circled Play-595b40b65ba036ed117d436f.svg);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0,0);}""QPushButton:pressed{image: url(./icons/Circled Play-595b40b65ba036ed117d436f.svg);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0)}")
        
        #self.threadAcq.terminate()    
        
    def Display(self,data):
        self.data=data
        if self.checkBoxScale.isChecked()==1: # autoscale on
            self.imh.setImage(data.astype(float),autoLevels=True,autoDownsample=True)
            
        else :
            self.imh.setImage(data.astype(float),autoLevels=False,autoDownsample=True)
            
        
        if self.winM.isWinOpen==True: #  measurement update
            self.Measurement()
    
        
    def bloquer(self): # bloque la croix 
        self.bloqq=1
        self.confCCD.setValue(self.nbcam+"/xc",int(self.xc)) # save cross postion in ini file
        self.confCCD.setValue(self.nbcam+"/yc",int(self.yc))
        print('xc',self.xc,'yc',self.yc)
        
        
    def debloquer(self): # deblaoque la croix : elle bouge avec la souris
        self.bloqq=0
    
    def roiChanged(self):
        self.rx=self.ro1.size()[0]
        self.ry=self.ro1.size()[1]
        self.confCCD.setValue(self.nbcam+"/rx",int(self.rx))
        self.confCCD.setValue(self.nbcam+"/ry",int(self.ry))
        
        
    def mouseMoved(self,evt):
        ## pour que la cross suive le mvt de la souris
        if self.bloqq==0: # souris non bloquer
            pos = evt[0]  ## using signal proxy turns original arguments into a tuple
            if self.p1.sceneBoundingRect().contains(pos):
                mousePoint = self.vb.mapSceneToView(pos)
                self.xc = (mousePoint.x())
                self.yc= (mousePoint.y())
                if ((self.xc>0 and self.xc<self.data.shape[0]) and (self.yc>0 and self.yc<self.data.shape[1]) ):
                        self.vLine.setPos(self.xc)
                        self.hLine.setPos(self.yc) # la croix ne bouge que dans le graph       
                        self.ro1.setPos([self.xc-(self.rx/2),self.yc-(self.ry/2)])
                        
    
    
            
    def paletteup(self):
        levels=self.imh.getLevels()
        if levels[0]==None:
            xmax =self.data.max()
            xmin=self.data.min()
        else :
            xmax=levels[1]
            xmin=levels[0]
            
        self.imh.setLevels([xmin, xmax+(xmax- xmin) / 10])
        #hist.setImageItem(imh,clear=True)
        self.hist.setHistogramRange(xmin,xmax)

    def palettedown(self):
        levels=self.imh.getLevels()
        if levels[0]==None:
            xmax=self.data.max()
            xmin=self.data.min()
        else :
            xmax=levels[1]
            xmin=levels[0]
            
        self.imh.setLevels([xmin, xmax- (xmax- xmin) / 10])
        #hist.setImageItem(imh,clear=True)
        self.hist.setHistogramRange(xmin,xmax)
    
    
    def open_widget(self,fene):
        """ open new widget 
        """

        if fene.isWinOpen==False:
            fene.setup
            fene.isWinOpen=True
            
            #fene.Display(self.data)
            fene.show()
        else:
            #fene.activateWindow()
#            fene.raise_()
#            fene.showNormal()
            pass
            
    def Measurement(self) :
        self.winM.setFile(self.camName)
        self.open_widget(self.winM)
        self.winM.Display(self.data)
        
    def closeEvent(self,event):
        self.fin()
        event.accept()
    
    
    def fin(self):
        try :
            self.threadRunAcq.stopThreadRunAcq()
        except :
            pass
        try :
            self.cam0.close()
        except :
            pass
        exit  
        
        
class ThreadRunAcq(QtCore.QThread):
    
    newDataRun=QtCore.Signal(object)
    
    def __init__(self, parent=None):
        
        super(ThreadRunAcq,self).__init__(parent)
        self.parent=parent
        self.cam0 = self.parent.cam0
        self.stopRunAcq=False
        self.itrig= self.parent.itrig
        
    def run(self):
        
        global data
        self.cam0.reset_frame_ready()
        self.cam0.start_live(show_display=False)
        self.cam0.enable_trigger(True)
        if not self.cam0.callback_registered:
            self.cam0.register_frame_ready_callback()
            
            
        #print('-----> Start  multi acquisition')
        
        while True :
            self.cam0.reset_frame_ready()
            if self.stopRunAcq:
                break
            
            #print('-----> Acquisition ended')
            
            if self.itrig==0: # si cam pas en mode trig externe on envoi un trig soft...
                self.cam0.send_trigger()
               # print('trigg')
            self.cam0.wait_til_frame_ready(2000)
            data1 = self.cam0.get_image_data() 
            data1 = np.array(data1)#, dtype=np.double)
            data1.squeeze()
            data=data1[:,:,0]
            data=np.rot90(data,1)
            self.newDataRun.emit(data)
    
    def stopThreadRunAcq(self):
        #self.cam0.send_trigger()
        try :
            self.stopRunAcq=True
        except : 
            pass
        self.cam0.stop_live()
        
class ThreadOneAcq(QtCore.QThread):
    
    newDataOne=QtCore.Signal(object)
    
    def __init__(self, parent=None):
        
        super(ThreadOneAcq,self).__init__(parent)
        self.parent=parent
        self.cam0 = self.parent.cam0
        self.stopOneAcq=False
        self.itrig= self.parent.itrig
        
    def run(self):
        
        global data
        self.cam0.reset_frame_ready()
        self.cam0.start_live(show_display=False)
        self.cam0.enable_trigger(True)
        if not self.cam0.callback_registered:
            self.cam0.register_frame_ready_callback()
            
      
        
        self.cam0.reset_frame_ready()
     
        
        if self.itrig==0: # si cam pas en mode trig externe on envoi un trig soft...
            self.cam0.send_trigger()
           # print('trigg')
        self.cam0.wait_til_frame_ready(2000)
        data1 = self.cam0.get_image_data() 
        data1 = np.array(data1)#, dtype=np.double)
        data1.squeeze()
        data=data1[:,:,0]
        data=np.rot90(data,1)
        self.newDataOne.emit(data)
        print('send data one acq')
        self.cam0.stop_live()
        print('stop one acq')
        
    def stopThreadOneAcq(self):
        #self.cam0.send_trigger()
        try :
            self.stopOneAcq=True
        except : 
            pass
        self.cam0.stop_live()

if __name__ == "__main__":
    appli = QApplication(sys.argv)  
    e = CameraAcqD(name='cam0',visuGauche=True)  
    e.show()
    appli.exec_()         