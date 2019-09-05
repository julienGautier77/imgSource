#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 27 17:07:24 2019

pip install qdarkstyle
pip install pyqtgraph


@author: juliengautier

"""
version='ImgSource_2019.9'


from PyQt5.QtWidgets import QApplication,QVBoxLayout,QHBoxLayout,QWidget,QPushButton
from PyQt5.QtWidgets import QComboBox,QSlider,QLabel,QSpinBox
from pyqtgraph.Qt import QtCore
from PyQt5.QtCore import Qt
import sys,time
import numpy as np
import qdarkstyle
from visu import SEE
try :
    import IC_ImagingControl 
    ic_ic = IC_ImagingControl.IC_ImagingControl()
    ic_ic.init_library()
except :
    'probleme importation IC_ImagingControl'
    pass

#self._single_frame.wait_for_capture(1000000)

#"a0=str(conf.value(nbcam+"/serial"))
#print('a0',a0)
#cam0=Vimba().camera(cameraIds[0])#(str(conf.value(nbcam+"/serial")))## pour prendre la premiere camera presente : cam0=Vimba().getCamera(cameraIds[0]) 
#print ("Device n :" , cameraIds[0])


class IMGSOURCE(QWidget):
    def __init__(self,cam='camDefault'):
        super(IMGSOURCE, self).__init__()
        
        self.confCCD=QtCore.QSettings('confCCD.ini', QtCore.QSettings.IniFormat)
        self.setWindowTitle(version)
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.nbcam=cam
        self.initCam()
        self.setup()
        self.itrig=0
        self.actionButton()
        self.camIsRunnig=False
    def initCam(self):
        
        if self.nbcam=='camDefault':    
            cam_names=ic_ic.get_unique_device_names()
            self.camID=str(cam_names[0].decode())
            self.cam0=ic_ic.get_device((self.camID.encode()))
            self.ccdName='CAM0'
        else :
            self.camID=self.confCCD.value(self.nbcam+"/camID")
            try :
                self.cam0=ic_ic.get_device((self.camID.encode()))
                self.ccdName=self.confCCD.value(self.nbcam+"/nameCDD")
            except: # si la camera n'existe pas on ouvre la premiere 
                self.nbcam='camDefault'
                cam_names=ic_ic.get_unique_device_names()
                self.camID=str(cam_names[0].decode())
                self.cam0=ic_ic.get_device((self.camID.encode()))
                self.ccdName='CAM0'
            
            print(self.ccdName, 'is connected @:'  ,self.camID )
           
        self.setWindowTitle(self.ccdName+'       v.'+ version)
        
        self.cam0.open()
        
        self.cam0.enable_continuous_mode(True)
        self.cam0.gain.auto=False
        self.cam0.exposure.auto=False
        self.cam0.set_frame_rate=float(25)
        frameRate=self.cam0.get_frame_rate()
        print('frame rate=',frameRate)
        sh=int(self.confCCD.value(self.nbcam+"/shutter"))
        self.cam0.exposure.value=int(sh)
        g=int(self.confCCD.value(self.nbcam+"/gain"))
        self.cam0.gain.value=int(g)
       
        
        
    def setup(self):   
        
        cameraWidget=QWidget()
        vbox1=QVBoxLayout() 
        #vbox1.addStretch(1)
        
        self.camName=QLabel(self.ccdName,self)
        self.camName.setAlignment(Qt.AlignCenter)
        
        self.camName.setStyleSheet('font :bold  30pt;color: white')
        vbox1.addWidget(self.camName)
        
        hbox1=QHBoxLayout() # horizontal layout pour run et stop
        self.runButton=QPushButton(self)
        self.runButton.setMaximumWidth(60)
        self.runButton.setMinimumHeight(60)
        self.runButton.setStyleSheet("QPushButton:!pressed{border-image: url(./icons/Circled Play-595b40b65ba036ed117d436f.svg);background-color: rgb(0, 0, 0,0) ;border-color: green;}""QPushButton:pressed{image: url(./icons/Circled Play-595b40b65ba036ed117d436f.svg);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0)}")
        self.stopButton=QPushButton(self)
        
        self.stopButton.setMaximumWidth(60)
        self.stopButton.setMinimumHeight(60)
        self.stopButton.setStyleSheet("QPushButton:!pressed{border-image: url(./icons/Stop.svg);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0,0);}""QPushButton:pressed{image: url(./icons/Stop.svg);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0)}")
        self.stopButton.setEnabled(False)
        
        hbox1.addWidget(self.runButton)
        hbox1.addWidget(self.stopButton)
        
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
        
        self.labelExp=QLabel('Exposure (ms)')
        self.labelExp.setMaximumWidth(120)
        self.labelExp.setAlignment(Qt.AlignCenter)
        vbox1.addWidget(self.labelExp)
        self.hSliderShutter=QSlider(Qt.Horizontal)
        self.hSliderShutter.setMinimum(self.cam0.exposure.min)
        self.hSliderShutter.setMaximum(self.cam0.exposure.max)
        self.hSliderShutter.setValue(int(self.confCCD.value(self.nbcam+"/shutter")))
        self.hSliderShutter.setMaximumWidth(80)
        self.shutterBox=QSpinBox()
        self.shutterBox.setMinimum(self.cam0.exposure.min)
        self.shutterBox.setMaximum(self.cam0.exposure.max)
        self.shutterBox.setMaximumWidth(60)
        self.shutterBox.setValue(int(self.confCCD.value(self.nbcam+"/shutter")))
        hboxShutter=QHBoxLayout()
        hboxShutter.addWidget(self.hSliderShutter)
        hboxShutter.addWidget(self.shutterBox)
        vbox1.addLayout(hboxShutter)
        
        self.labelGain=QLabel('Gain')
        self.labelGain.setMaximumWidth(120)
        self.labelGain.setAlignment(Qt.AlignCenter)
        vbox1.addWidget(self.labelGain)
        hboxGain=QHBoxLayout()
        self.hSliderGain=QSlider(Qt.Horizontal)
        self.hSliderGain.setMaximumWidth(80)
        self.hSliderGain.setMinimum(self.cam0.gain.min)
        self.hSliderGain.setMaximum(self.cam0.gain.max)
        self.hSliderGain.setValue(int(self.confCCD.value(self.nbcam+"/gain")))
        self.gainBox=QSpinBox()
        self.gainBox.setMinimum(self.cam0.gain.min)
        self.gainBox.setMaximum(self.cam0.gain.max)
        self.gainBox.setMaximumWidth(60)
        self.gainBox.setValue(int(self.confCCD.value(self.nbcam+"/gain")))
        hboxGain.addWidget(self.hSliderGain)
        hboxGain.addWidget(self.gainBox)
        vbox1.addLayout(hboxGain)
        
        self.TrigSoft=QPushButton('Trig Soft',self)
        self.TrigSoft.setMaximumWidth(100)
        vbox1.addWidget(self.TrigSoft)
        
        vbox1.addStretch(1)
        
        cameraWidget.setLayout(vbox1)
        cameraWidget.setMinimumSize(150,200)
        cameraWidget.setMaximumSize(200,900)
        hMainLayout=QHBoxLayout()
        hMainLayout.addWidget(cameraWidget)
        
        
        self.visualisation=SEE()
        
        vbox2=QVBoxLayout() 
        vbox2.addWidget(self.visualisation)
        hMainLayout.addLayout(vbox2)
        
        self.setLayout(hMainLayout)
        
        
    def actionButton(self):
        self.runButton.clicked.connect(self.acquireMultiImage)
        self.stopButton.clicked.connect(self.stopAcq)      
        self.shutterBox.editingFinished.connect(self.shutter)    
        self.hSliderShutter.sliderReleased.connect(self.mSliderShutter)
        
        self.gainBox.editingFinished.connect(self.gain)    
        self.hSliderGain.sliderReleased.connect(self.mSliderGain)
        self.trigg.currentIndexChanged.connect(self.trigA)
        
        self.TrigSoft.clicked.connect(self.softTrigger)
    
    
    def softTrigger(self):
        self.cam0.send_trigger()
        
    
    def shutter (self):
        sh=self.shutterBox.value() # lit valeur de la box
        self.hSliderShutter.setValue(sh) # set value du slider
        time.sleep(0.1)
        self.cam0.exposure.auto=False
        self.cam0.exposure.value=int(sh)
        self.confCCD.setValue(self.nbcam+"/shutter",float(sh))
        self.confCCD.sync()
    
    def mSliderShutter(self):
        sh=self.hSliderShutter.value() #lit valeur Slider 
        self.shutterBox.setValue(sh) # set valeur de la box
        time.sleep(0.1)
        self.cam0.exposure.value=int(sh)
        self.confCCD.setValue(self.nbcam+"/shutter",float(sh))
    
    def gain (self):
        g=self.gainBox.value() # lit valeur de la box
        self.hSliderGain.setValue(g) # set value du slider
        time.sleep(0.1)
        self.cam0.gain.value=int(g)
        self.confCCD.setValue(self.nbcam+"/gain",float(g))
        self.conf.sync()
    
    def mSliderGain(self):
        g=self.hSliderGain.value() #lit valeur Slider 
        self.gainBox.setValue(g) # set valeur de la box
        time.sleep(0.1)
        self.cam0.gain.value=int(g)
        self.confCCD.setValue(self.nbcam+"/gain",float(g))
        self.confCCD.sync()
        
    def trigA(self):
        self.itrig=self.trigg.currentIndex()
        if self.itrig==1:
           self.cam0.enable_trigger(True)
        else:
            self.cam0.enable_trigger(False)
            
            
    def acquireMultiImage(self):     
        
        self.runButton.setEnabled(False)
        self.runButton.setStyleSheet("QPushButton:!pressed{border-image: url(./icons/Circled Play-595b40b65ba036ed117d436f.svg);background-color: gray ;border-color: rgb(0, 0, 0,0);}""QPushButton:pressed{image: url(./icons/Circled Play-595b40b65ba036ed117d436f.svg);background-color: gray ;border-color: rgb(0, 0, 0)}")
        
        self.stopButton.setEnabled(True)
        self.stopButton.setStyleSheet("QPushButton:!pressed{border-image: url(./icons/Stop.svg);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0,0);}""QPushButton:pressed{image: url(./icons/Stop.svg);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0)}")
        
        self.trigg.setEnabled(False)
        self.threadRunAcq=ThreadRunAcq(cam0=self.cam0,itrig=self.itrig)
        self.threadRunAcq.newDataRun.connect(self.Display)
        self.threadRunAcq.start()   
        self.camIsRunnig=True
    
    def stopAcq(self):
        print('stop')
        if self.camIsRunnig==True:
            self.threadRunAcq.stopThreadRunAcq()
            self.camIsRunnig=False
            
        self.runButton.setEnabled(True)
        self.runButton.setStyleSheet("QPushButton:!pressed{border-image: url(./icons/Circled Play-595b40b65ba036ed117d436f.svg);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0,0);}""QPushButton:pressed{image: url(./icons/Circled Play-595b40b65ba036ed117d436f.svg);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0)}")
        self.stopButton.setEnabled(False)
        self.stopButton.setStyleSheet("QPushButton:!pressed{border-image: url(./icons/Stop.svg);background-color: gray ;border-color: rgb(0, 0, 0,0);}""QPushButton:pressed{image: url(./icons/Stop.svg);background-color: gray ;border-color: rgb(0, 0, 0)}")
        
        self.trigg.setEnabled(True)
        
        
    def Display(self,data):
        self.data=data
        self.visualisation.newDataReceived(self.data)
        
    def closeEvent(self,event):
        print(' close')
        self.stopAcq()
        time.sleep(0.1)
        self.cam0.close()
        
        
        
class ThreadRunAcq(QtCore.QThread):
    
    newDataRun=QtCore.Signal(object)
    
    def __init__(self, parent=None,cam0=None,itrig=None):
        
        super(ThreadRunAcq,self).__init__(parent)
        self.cam0 = cam0
        self.stopRunAcq=False
        self.itrig= itrig
        
    def run(self):
        

        self.cam0.reset_frame_ready()
        self.cam0.start_live(show_display=False)
        self.cam0.enable_trigger(True)
        if not self.cam0.callback_registered:
            self.cam0.register_frame_ready_callback()
            
            
        #print('-----> Start  multi acquisition')
        
        while self.stopRunAcq is not True:
            self.cam0.reset_frame_ready()
            
            if self.itrig==0: # si cam pas en mode trig externe on envoi un trig soft...
                self.cam0.send_trigger()
               # print('trigg')
            self.cam0.wait_til_frame_ready(20000)
            dat1 = self.cam0.get_image_data() 
            if dat1 is not None:
                data1 = np.array(dat1, dtype=np.double)
                data1.squeeze()
                data=data1[:,:,0]
                data=np.rot90(data,1)
                if self.stopRunAcq==True:
                    pass
                else:
                    self.newDataRun.emit(data)
    
    def stopThreadRunAcq(self):
        self.stopRunAcq=True
        self.cam0.send_trigger()
        self.cam0.stop_live()

        
    
if __name__ == "__main__":       
    
    appli = QApplication(sys.argv) 
    appli.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    e = IMGSOURCE('camDefault')  
    e.show()
    appli.exec_()       
    
    