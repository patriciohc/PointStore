from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ConfigParser
import sys
 
class ShowPrint(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        contenedor = QVBoxLayout()
        self.setLayout(contenedor) 
        self.textEdit = QTextEdit()
        contenedor.addWidget(self.textEdit)

        cfg = ConfigParser.ConfigParser()
        cfg.read(["./config.cfg"])
        if cfg.has_option("pointstore", "name"):
            self.name = cfg.get('pointstore','name')
        if cfg.has_option("pointstore",'address'):
            self.address = cfg.get('pointstore','address')
        if cfg.has_option("pointstore", 'url'):
            self.url = cfg.get('pointstore','url')
        if cfg.has_option("pointstore", 'otherInfo'):
            self.otherInfo = cfg.get('pointstore','otherInfo')


    def setTextB(self, fecha, no_nota, basket, total, recibo, cambio):
        f = "<h3>%s</h3>" %(self.name)
        f += self.subString(self.address)
        f += "Fecha: %s \n" % (fecha)
        f += "Nota: %s \n" % (no_nota)
        f += "--------------------------------------------\n"
        for prod in basket:
            f += prod[2]+"\n" # nombre produto
            # cantidad
            f += `prod[1]`+"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;x&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            # precio unitario e importe
            f += `prod[3]`+"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"+`prod[4]`+'\n'
        f += "<h4>Subtotal: &nbsp;&nbsp;" +str(total)+ "</h4>\
            <h4>Descuento: &nbsp;&nbsp;0%</h4>\
            <h4>TOTAL: &nbsp;&nbsp;"+str(total)+"</h4>"
        f += self.subString(self.otherInfo)
        f += "--------------------------------------------\n"
        f = f.replace("\n","<br>")
        self.textEdit.setText(f)

    def setText(self,nota):
        f = "<h3>%s</h3>" %(self.name)
        f += self.subString(self.address)
        f += "Fecha: %s \n" % (nota.fecha)
        f += "Nota: %s \n" % (nota.id)
        f += "--------------------------------------------\n"
        for pn in nota.productos:
            f += pn.producto.descripcion+"\n" # nombre produto
            # cantidad
            f += `pn.cantidad`+"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;x&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            # precio unitario e importe
            f += `pn.precio_publico`+"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"+`float(pn.cantidad)*float(pn.precio_publico)`+'\n'
        f += "<h4>Subtotal: &nbsp;&nbsp;" +str(nota.total)+ "</h4>\
            <h4>Descuento: &nbsp;&nbsp;0%</h4>\
            <h4>TOTAL: &nbsp;&nbsp;"+str(nota.total)+"</h4>"
        f += self.subString(self.otherInfo)
        f += "--------------------------------------------\n"
        f = f.replace("\n","<br>")
        self.textEdit.setText(f)


    def subString(self, string):
        sub = ""
        n = 0
        ancho = 32 # ancho de tiket, 32 caracteres aprox.
        while n < len(string):
            sub += string[n:n+ancho] + "\n"
            n = n + ancho
        return sub

