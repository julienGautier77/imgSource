# imgSource


imgSource  is an user interface library to control imaging Source camera.

it uses ic-imaging-control from : 

    https://github.com/morefigs/py-ic-imaging-control

It can make plot profile and data measurements  analysis

    https://github.com/julienGautier77/imgSource

## Requirements

*  install Download the IC Imaging Control C SDK from here:
    http://www.theimagingsource.com/en_US/support/downloads/details/icimagingcontrolcwrapper/
*   python 3.x
*   Numpy
*   PyQt5
*   visu
    https://github.com/julienGautier77/visu.git
    


## Usage

    from PyQt5.QtWidgets import QApplication
    import sys
    import qdarkstyle
    import andor
    
    appli = QApplication(sys.argv)   
    appli.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    e = IMGSOURCE('camDefault')
    e.show()
-----------------------------------------
-----------------------------------------
