from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ConfigParser
import sys
 
class ShowInfo(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        contenedor = QVBoxLayout()
        self.setLayout(contenedor) 
        self.info = QLabel()
        contenedor.addWidget(self.info)
        textocss = """
<h3 style='color:#0080FF'>Shell System</h3>
<h4 style='color:#000'>Carr. Fed Mex. Pue. Km 98 No 6</h4>
<h4 style='color:#000'>email: patriciohc.0@gmail.com</h4>
"""
        self.info.setText(textocss)


