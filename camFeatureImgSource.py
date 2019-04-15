# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 11:02:31 2019

@author: sallejaune
"""


try :
    import IC_ImagingControl 
    ic_ic = IC_ImagingControl.IC_ImagingControl()
    ic_ic.init_library()
except :
    'probleme importation IC_ImagingControl'
    pass

cam_names=ic_ic.get_unique_device_names()
camID=str(cam_names[0].decode())
cam0=ic_ic.get_device((camID.encode()))

cam0.open()
print(cam0.exposure.min)
for feature_name in cam0.list_property_names():
    print(feature_name)

cam0.close()