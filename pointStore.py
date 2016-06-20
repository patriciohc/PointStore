#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import sys, os, datetime, urllib2, tarfile
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ui_pointStore import Ui_Principal  
import sqlite3, ConfigParser  
from bs4 import BeautifulSoup # uitlizado para obtener biografias desde una pagian web
from urllib2 import urlopen # uitlizado para obtener biografias desde una pagian web
import random
import hashlib
from uuid import getnode as get_mac

import dataBase
from productsList import ProductsList
from showPrint import ShowPrint
from notas import ListaNotas, Nota
from nosotros import ShowInfo



class ingreso(QMainWindow, Ui_Principal):
    def __init__(self):
        autorized = 80067394566866L
        QDialog.__init__(self)
        msgTitle = "Error!"
        msg = "no se ha podido establecer conexion con base de datos!"
        msgCopyNoValid = "La copia de este software no es valida!\n Contactenos para mayor informacion <patriciohc.0@gmail.com>"
        self.setupUi(self)
        self.stack.setCurrentIndex(0)
        self.db =  dataBase.dataBase()
        cod = get_mac()
        if cod != autorized:
            QMessageBox.critical(self, msgTitle, msgCopyNoValid)
            exit()
        if not self.db.connect():
            QMessageBox.critical(self, msgTitle, msg)
            exit()
        self.productsList = ProductsList(self.db)
        self.listNotas = ListaNotas(self.db)
        self.showPrint = ShowPrint()
        nota = self.db.fetchone("select `id` from notas order by `id` desc limit 1;")
        self.nota=str(nota[0])
        self.lnota.setText("Ultima Nota: <b>#"+self.nota+"</b>")
        self.nFecha = 0

#### botones #####
        self.connect(self.blimpiar, SIGNAL("clicked()"), self.limpiar)
        self.connect(self.btNuevaLam, SIGNAL("clicked()"), self.add_lamina)
        self.connect(self.bpgenera, SIGNAL("clicked()"), self.gencode)
# boton que agrega nuevo producto
        self.connect(self.bpagregar, SIGNAL("clicked()"), self.add_producto)
#### edit text (cajas de texto)
        self.connect(self.codigo, SIGNAL("editingFinished()"), self.display)
        self.connect(self.codigo, SIGNAL("textChanged(QString)"), self.busca1)
        self.connect(self.cant, SIGNAL("returnPressed()"), self.agregar)
        self.connect(self.ttext, SIGNAL("textChanged(QString)"), self.busk)
        self.connect(self.tpcodigo, SIGNAL("editingFinished()"), self.setFocus1)
        self.connect(self.tpdesc, SIGNAL("editingFinished()"), self.setFocus2)
        self.connect(self.cpdep, SIGNAL("returnPressed()"), self.setFocus3)
        self.connect(self.txtPrecio, SIGNAL("editingFinished()"), self.setFocus4)
        self.connect(self.txtPrecioPublico, SIGNAL("returnPressed()"), self.add_producto)
# buscador de productos, laminas y biografias 
        self.connect(self.ttext, SIGNAL("returnPressed()"), self.busk_bio)
# buscador de productos para edicion
        self.connect(self.tfiltro, SIGNAL("editingFinished()"), self.listarps)
# buscaodor de laminas para edicion 
        self.connect(self.txtFilterLam, SIGNAL("editingFinished()"), self.listaLaminas)
        self.connect(self.txtCodigoLam, SIGNAL("returnPressed()"), self.add_lamina)  
        self.connect(self.txtTituloLam, SIGNAL("returnPressed()"), self.add_lamina)
#### radio check #####
        self.connect(self.rlam, SIGNAL("clicked()"), self.busk)
        self.connect(self.rbio, SIGNAL("clicked()"), self.busk_bio)
        self.connect(self.rtemp, SIGNAL("clicked()"), self.descuento)
        self.connect(self.rmen, SIGNAL("clicked()"), self.descuento)
        self.connect(self.rmay, SIGNAL("clicked()"), self.descuento)
        self.connect(self.rprod, SIGNAL("clicked()"), self.busk)
#### tablas ####
# tabla laminas para edicion
        self.connect(self.tbLaminas, SIGNAL("doubleClicked(QModelIndex)"), self.editLam)  
# tabla laminas para edicion
        self.connect(self.tbLaminas, SIGNAL("itemActivated(QTableWidgetItem*)"), self.editLam)
# tabla de productos para edicion
        self.connect(self.tplista, SIGNAL("doubleClicked(QModelIndex)"), self.editItem)
### QToolButton (botones de la parte superior)
        self.connect(self.beliminar, SIGNAL("clicked()"), self.delete)
        self.connect(self.bbuska, SIGNAL("clicked()"), self.buskador)
        self.connect(self.bventa, SIGNAL("clicked()"), self.ventaOn)
        self.connect(self.badmin, SIGNAL("clicked()"), self.adminOn)
        self.connect(self.btCorteCaja, SIGNAL("clicked()"), self.corteOn)
# cierre de venta
        self.connect(self.btCerrarVenta, SIGNAL("clicked()"), self.cierre_venta)
### calendario ###
        self.connect(self.calendario, SIGNAL('clicked(QDate)'), self.event_cal)
### Menu ###
        self.connect(self.actionBuscador, SIGNAL("triggered()"), self.buskador)
        self.connect(self.actionImprimir, SIGNAL("triggered()"), self.imprimir)
        self.connect(self.actionCorte, SIGNAL("triggered()"), self.corteOn)
        self.connect(self.actionAdministrador, SIGNAL("triggered()"), self.adminOn)
        self.connect(self.actionNueva, SIGNAL("triggered()"), self.ventaOn)
        self.connect(self.actionEditar_nota, SIGNAL("triggered()"), self.abrirNota)
        self.connect(self.actionGuardar, SIGNAL("triggered()"), self.guardarNota)
        self.connect(self.actionGuardar, SIGNAL("triggered()"), self.guardarNota)
        self.connect(self.actionAcerca, SIGNAL("triggered()"), self.showInfo)

        self.connect(self.lista2, SIGNAL("doubleClicked(QModelIndex)"), self.adomatic)
        #self.connect(self.lista2, SIGNAL("itemActivated(QListWidgetItem*)"), self.adomatic)
        self.connect(self.tbusk, SIGNAL("doubleClicked(QModelIndex)"), self.adomatic)
        #self.connect(self.tbusk, SIGNAL("itemActivated(QTableWidgetItem*)"), self.adomatic)

        self.cliente=[0,"Normal mostrador",'','','']
        self.basket=[]
        self.tipo=0
        self.codigo.setFocus()
        self.txt=""
        self.desc=0
        self.hoy=datetime.date.today()
        self.lfecha.setText("Fecha: <b>"+str(self.hoy.strftime("%d/%m/%Y"))+"</b>")
        self.fecha=str(self.hoy.strftime("%Y-%m-%d"))
        day=self.hoy.strftime("%d")


    def adomatic(self):
        if (self.stack.currentIndex()!=0):
            if (self.rprod.isChecked()):
                item=self.tbusk.item(self.tbusk.currentRow(),0)
                desc=self.tbusk.item(self.tbusk.currentRow(),1)
                ref=str(item.text())
            elif (self.rlam.isChecked() ):
                ref='LAMINA'
            elif (self.rbio.isChecked() ):
                ref='BIOGRAFIA'
            self.stack.setCurrentIndex(0)
            self.txt=ref
            self.ttext.setText('')
            self.sec1(ref)
            self.codigo.clear()
            self.cant.setFocus()
            self.cant.setText("1")
            self.cant.selectAll()
        else:
            self.txt=str(self.refs[self.lista2.currentRow()])
            ref=self.txt
            self.sec1(ref)
            self.codigo.clear()
            self.cant.setFocus()
            self.cant.setText("1")
            self.cant.selectAll()

    #def on_context_menu(self, point):
    #    self.popMenu.exec_( self.lista2.mapToGlobal(point) )

    def buskador(self):
        if (self.stack.currentIndex()!=1):
            self.stack.setCurrentIndex(1)
            self.ttext.setFocus()
        else:
            self.stack.setCurrentIndex(0)
            self.codigo.setFocus()

    def ventaOn(self):
        if (self.stack.currentIndex()!=0):
            self.stack.setCurrentIndex(0)
            self.codigo.setFocus()

# realiza corte de caja
    def corteOn(self):
        msgTitle = self.tr("Acceso Restringido")
        msg = self.tr("Ingrese su clave de autorizacion.")
        tkey = QLineEdit()
        tkey.setEchoMode(QLineEdit.Password)
        Acceso = QInputDialog.getText(self, msgTitle, msg, QLineEdit.Password)
        if(self.aut(Acceso[0])): 
            if (self.stack.currentIndex()!=3):    
                self.stack.setCurrentIndex(3)
                self.event_cal()

    def adminOn(self):
        tkey = QLineEdit()
        tkey.setEchoMode(QLineEdit.Password)
        Acceso = QInputDialog.getText(self, self.tr("Acceso Restringido"),self.tr("Ingrese su clave de autorizacion."),QLineEdit.Password)                         
        if(self.aut(Acceso[0])):
            if (self.stack.currentIndex()!=2):
                self.stack.setCurrentIndex(2)
        else:
            self.stack.setCurrentIndex(0)
            self.codigo.setFocus()

    def webOn(self):
        if (self.stack.currentIndex()!=3):
            self.stack.setCurrentIndex(3)
        else:
            self.stack.setCurrentIndex(0)
            self.codigo.setFocus()
    #d = buscador()
    #d.show()
    #d.connect(d.lista1, SIGNAL("doubleClicked(QModelIndex)"), self.muestra)
    #print x
    #d.exec_()

# funcion que permite el acceso a administrador
    def aut(self, key, user='admin'):
        hash_key = hashlib.sha1(str(key))
        hex_key = hash_key.hexdigest()
        query = "select level, pasword from usuarios where user='%s';" % (user)
        val = self.db.fetchone(query)
        try:
            # contraseña correcta y tiene permisos de administrador
            if hex_key == val[1] and val[0] == 3:
                return True
            else:  
                return False
            # no regreso ningun usuario
        except TypeError: 
            return False

# abre nota desde archivo de texto
    def abrirNota(self):
        dirBase = './'
        fileName = QFileDialog.getOpenFileName(self, 'Seleccione una nota', dirBase, selectedFilter='*.txt')
        if not fileName:
            return
        f = open(fileName)
        linea =  f.readline()
        msg = "El archivo no pudo ser cargado completamente por que contien datos no validos"
        while linea != "":
            datos = linea.split(' ')
            if len(datos) != 2:
                QMessageBox.information(self, "Aviso", msg)
                return 
            try:
                ref = float(datos[0])
                cantidad = float(datos[1])
            except ValueError:
                QMessageBox.information(self, "Aviso", msg)
                return
            pList = ProductsList()
            p = pList.findProduct(ref)
            tupla = [p.id, cantidad, p.descripcion, p.precio_publico, cantidad * float(p.precio_publico)]
            self.ingreso(tupla)
            linea = f.readline()
        f.close()

# Cierra la venta, guarda la nota en la base de datos e inicia el proceso de impresion
    def guardarNota(self):
        dirBase = './'
        fileName = QFileDialog.getSaveFileName(self, 'Guardar', dirBase, selectedFilter='*.txt')
        f = open(fileName,'w')
        for p in self.basket:
            f.write(str(p[0])+' '+str(p[1])+'\n')
        f.close()

# Busca biografias desde sitio web, muestra la informacion usando webscrapin
    def busk_bio(self):
        txt=str(self.ttext.text())
        tem = txt.split(' ')
        n = len(tem)
        if n > 1:
            txt = '' 
            for p in tem:
                txt = txt+p+'+'
            txt = txt[0:-1]
        print txt
        if self.rbio.isChecked():
            url = 'http://www.grupoeditorialraf.com/raf/html/buscador-paso1.php?buscar='+txt+'&bio=1&seccion=0&grado=elija&Enviar=Buscar'
            n = 3
        elif self.rlam.isChecked():
            url = 'http://www.grupoeditorialraf.com/raf/html/buscador-paso1.php?buscar='+txt+'&mono=1&seccion=0&grado=elija&Enviar=Buscar'
            n = 2
        else:
            return
        print url
        head=('Codigo','Nombre')
        soup =  BeautifulSoup(urlopen(url))
        current = soup.find_all('tr')
        self.tbusk.setColumnCount(len(head))
        self.tbusk.setRowCount(0)     
        self.tbusk.setRowCount(len(current))     
            #agrega nombre de columnas
        for i,data in enumerate(head): 
            item = QTableWidgetItem(1)
            item.setText(str(data))
            self.tbusk.setHorizontalHeaderItem(i,item)
        i = 1
        t =  len(current)
        j = 0;
        print t
        while i < t: 
            fila = current[i]
            soup1 =  BeautifulSoup(str(fila))
            codigo = soup1.find_all('td')[0].renderContents()
            nombre = soup1.find_all('td')[1].renderContents()
            #print codigo, nombre
            #for j,data in enumerate(elem):
            item = QTableWidgetItem(1)
            text = ("   %s \t") % codigo
            item.setText(text)
            self.tbusk.setItem(j,0,item)
            item = QTableWidgetItem(1)
            text = ("   %s \t") % nombre.decode("utf8")
            item.setText(text)
            self.tbusk.setItem(j,1,item)
            i = i + n
            j = j + 1
        self.tbusk.resizeColumnsToContents()   
        #print current[0].contents


    def busk(self): # busca
        txt=str(self.ttext.text())
        if (self.rlam.isChecked()): #laminas
            sql="SELECT numero, titulo FROM laminas where `titulo` like '%"+txt+"%' limit 50"
            head=('Codigo','Nombre')
        elif (self.rprod.isChecked()): #productos
            sql="SELECT `id`,`descripcion`,`precio_publico` FROM productos where descripcion like '%"+txt+"%' limit 50"
            head=('Ref','Descripcion','Precio publico')
        else: 
            return
        self.tbusk.setRowCount(0)
        result = self.db.fetchall(sql)
        self.tbusk.setColumnCount(len(head))
        self.tbusk.setRowCount(len(result))     
     
    #agrega nombre de columnas
        for i,data in enumerate(head): 
            item = QTableWidgetItem(1)
            item.setText(str(data))
            self.tbusk.setHorizontalHeaderItem(i,item)

        for i,elem in enumerate(result):
            for j,data in enumerate(elem):
                item = QTableWidgetItem(1)
                name_lam = ("   %s \t") % (data)
                item.setText(name_lam)
                self.tbusk.setItem(i,j,item)
        #item = QTableWidgetItem(1)
        #item.setText(str(data))
        #self.tabla.setItem(len(self.basket)-1,i , item)
        self.tbusk.resizeColumnsToContents()   

    def descuento(self):
        if (self.rtemp.isChecked()):
            self.desc=10
        elif (self.rmay.isChecked()):
            self.desc=15
        elif (self.rmen.isChecked()):
            self.desc=0
            self.grant()

    def busca1(self):
        txt = self.codigo.text()
        query = ("SELECT * FROM productos where `descripcion` like '%s' limit 15") % ("%"+txt+"%")
        result = self.db.fetchall(query)
        self.lista2.clear()
        self.refs=[]
        for rec in result:
            self.refs.append(int(rec[1]))
            #print rec[0] ,rec[1], rec[2]
            self.lista2.addItem(str(rec[2]))

      #self.connect(self.w,SIGNAL('customContextMenuRequested(QPoint)'), self.ctxMenu)


    def listaLaminas(self):
        txt=str(self.txtFilterLam.text())
        sql="SELECT numero, titulo FROM laminas where `titulo` like '%"+txt+"%' or numero='"+txt+"' limit 20"
        head=('Codigo','Titulo','Eliminar')
        result = self.db.fetchall(sql)
        self.tbLaminas.setColumnCount(len(head))
        self.tbLaminas.setRowCount(len(result))
        icon = QIcon("./images/16/delete_16.png")

        for i,data in enumerate(head):
            item = QTableWidgetItem(1)
            item.setText(str(data))
            self.tbLaminas.setHorizontalHeaderItem(i,item)
        for i,elem in enumerate(result):
            for j,data in enumerate(elem):
                item = QTableWidgetItem(1)
                label_item = ("%s") % (data)
                item.setText(label_item)
                self.tbLaminas.setItem(i,j,item)
            btEliminar = QPushButton("", None)
            btEliminar.setIcon(icon)
            #contenedor.addWidget(btnSalir)
            self.connect(btEliminar, SIGNAL("clicked()"), self.delete_lamina)
            self.tbLaminas.setCellWidget(i,2,btEliminar)
        self.tbLaminas.resizeColumnsToContents()   

    def delete_lamina(self):
        button = qApp.focusWidget()
        index = self.tbLaminas.indexAt(button.pos())
        if index.isValid():
            titulo = "%s" % self.tbLaminas.item(index.row(),1).text()
            reply = QMessageBox.question(self, 'Mensaje', "desea eliminar: "+titulo, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                query = "DELETE FROM laminas WHERE titulo='"+titulo+"';"
                #print query
                self.db.execute(query)
                self.db.commit();
                self.listaLaminas()

# agrega una nueva lamina
    def add_lamina(self):
        try:
            codigo = int(self.txtCodigoLam.text())
        except ValueError:
            QMessageBox.critical(self, "Error!", "el codigo debe ser un numero entero")
            return       
        titulo =  str(self.txtTituloLam.text())
        try:
            if titulo and codigo:
                query =  "insert into laminas(titulo,numero) values ('%s',%d)" % (titulo , codigo )
                print(query)
                self.db.execute(query)
                self.db.commit()
            else:
                QMessageBox.critical(self, "Error!", "ambos campos deben estar llenos!")
                return
        except sqlite3.Error, e:
            print "Error %s" % (e)
            QMessageBox.critical(self, "Error!", "No se ha podido agregar la nueva lamina\n verifique el no exista una lamina con el mismo nombre")
            return
        self.txtCodigoLam.setText('')
        self.txtTituloLam.setText('')
        self.listaLaminas()

# muestra lista de productos para edicion
    def listarps(self):
        txt=str(self.tfiltro.text())
        sql = "SELECT * FROM productos where descripcion like '%"+txt+"%' or codigo_bar='"+txt+"' or id='"+txt+"' limit 20"
        head = ('Referencia','Codigo','Descripcion','Departamento','Precio','Precio Publico','Eliminar')
        secciones =  ('abarrotes','papeleria','merceria','computo','regalos','oficina','servicios')
        result = self.db.fetchall(sql)
        icon = QIcon("./images/16/delete_16.png")
        self.tplista.setColumnCount(len(head))
        self.tplista.setRowCount(len(result))
        for i,data in enumerate(head):
            item = QTableWidgetItem(1)
            item.setText(str(data))
            self.tplista.setHorizontalHeaderItem(i,item)
        for i,elem in enumerate(result):
            for j,data in enumerate(elem):
                item = QTableWidgetItem(1)
                item.setText(str(data))
                self.tplista.setItem(i,j,item)
                self.tplista.resizeColumnsToContents()
# boton eleminar
            btEliminar = QPushButton("", None)
            btEliminar.setIcon(icon)
            self.connect(btEliminar, SIGNAL("clicked()"), self.delete_producto)
            self.tplista.setCellWidget(i,6,btEliminar)
# combobox para seleccionar departamento
            cmbSeccion = QComboBox()
            for s in secciones:
                cmbSeccion.addItem(s)
# busca item actual, la coloca en el combobox
            seccionAct = elem[3]
            for index, seccion in enumerate(secciones):
                if seccionAct.upper() == seccion.upper():
                    cmbSeccion.setCurrentIndex(index)
                    break
            self.connect(cmbSeccion, SIGNAL("currentIndexChanged(int)"), self.preSeccion)
            self.tplista.setCellWidget(i,3,cmbSeccion)

# prepara la actualizacion de la seccion
    def preSeccion(self):
        item = qApp.focusWidget()
        index = self.tplista.indexAt(item.pos())
        newSeccion = str(item.currentText())
        self.actProducto(index.column(), index.row(), newSeccion)

# edita un producto
    def editItem(self):
        msg = "Este texto reemplazara al valor seleccionado."
        item = self.tplista.currentItem()
        data = item.text()
        editor = QInputDialog.getText(self, self.tr("Editar celda"),self.tr(msg),QLineEdit.Normal, data)
        if editor[1]:
            col = self.tplista.currentColumn()
            row = self.tplista.currentRow()
            data = str(editor[0])
            self.actProducto(col, row, data)

# ejecuata la consulta para actualizar produto
    def actProducto(self, col, row, data):
        columnas = ('id','codigo_bar','descripcion','seccion','precio','precio_publico')
        item = self.tplista.currentItem()
        column = str(columnas[col])
        ref = self.tplista.item(row,0)
        sql = "UPDATE productos set `"+column+"`='"+data+"' WHERE id="+str(ref.text())+";"
        self.db.execute(sql)
        self.db.commit()
        self.listarps()


#elimina producto
    def delete_producto(self):
        button = qApp.focusWidget()
        index = self.tplista.indexAt(button.pos())
        if index.isValid():
            ref = "%s" % self.tplista.item(index.row(),0).text()
            reply = QMessageBox.question(self, 'Mensaje', "desea eliminar: "+ref, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                query = "DELETE FROM productos WHERE id="+ref+";"
                #print query
                self.db.execute(query)
                self.db.commit();
                self.listarps()

# edita lamina
    def editLam(self):
        columnas = ('titulo')
        codigo =  self.tbLaminas.item(self.tbLaminas.currentRow(),0).text()
        titulo = "%s" % self.tbLaminas.item(self.tbLaminas.currentRow(),1).text()
        print codigo, titulo
        editor = QInputDialog.getText(self, self.tr("Editar celda"),self.tr("Este texto reemplazara al valor seleccionado."),QLineEdit.Normal,titulo)
        if editor[1]:
            query = "UPDATE laminas set `titulo`='"+str(editor[0]).strip()+"' WHERE numero="+str(codigo)+";"
            print query
            self.db.execute(query)
            self.db.commit();
            self.listaLaminas()

# Cierra la venta, guarda la nota en la base de datos e inicia el proceso de impresion
    def cierre_venta(self):
        total = float(self.grant())
        if (self.rticket.isChecked()):
            while True:
                editor = QInputDialog.getText(self, self.tr("Cobrar"),self.tr("Cantidad recibida"),QLineEdit.Normal)
                if not editor[1]:
                    return
                try:
                    recibo = float(str(editor[0]))
                    if total > recibo:
                        QMessageBox.information(self, "Aviso", "Recibido es menor que total!")
                    else:
                        break
                except ValueError:
                    QMessageBox.critical(self, "Error!", "Ingrese un numero")
            cambio = recibo - total
            self.allocate(total, recibo, cambio)#Registra en base de datos
            QMessageBox.information(self,"Informacion", "cambio %.2f" % cambio)
            self.nota=self.db.fetchone("SELECT `id` from notas order by id desc limit 1")
            self.nota=self.nota[0]
            self.imprimir(self.nota, total, recibo, cambio)
            self.limpiar()
        elif self.rpresup.isChecked():
            self.imprimir(0, total, 0, 0)
            self.limpiar()

# se ejecuta siempre que se cambia la seleccion del calendario
    def event_cal(self):
        if self.rDia.isChecked():
            self.fechaIni = str(self.calendario.selectedDate().toPyDate())
            self.fechaFin = ""
            self.txtPeriodo.setText("Ventas del dia %s" % self.fechaIni)
            self.corte_caja()
        elif self.rPeriodo.isChecked():
            if self.nFecha == 0:
                self.fechaIni = str(self.calendario.selectedDate().toPyDate())
                self.nFecha += 1
            elif self.nFecha == 1:
                self.fechaFin = str(self.calendario.selectedDate().toPyDate())
                periodo = "Ventas del %s al %s" % (self.fechaIni, self.fechaFin)
                self.txtPeriodo.setText(periodo)
                self.corte_caja()
                self.nFecha = 0


    def corte_caja(self):
        if self.rDia.isChecked():
            self.listNotas.findNotas(self.fechaIni)
        elif self.rPeriodo.isChecked():
            self.listNotas.findNotas(self.fechaIni, self.fechaFin)
        head=('Nota','Fecha','Total vendido','Ganancia', 'Cancelar','')
        self.tbNotas.setRowCount(0)
        self.tbNotas.setColumnCount(len(head))
        self.tbNotas.setRowCount(self.listNotas.count())
# Agrega nombre de columnas
        for i,data in enumerate(head): 
            item = QTableWidgetItem(1)
            item.setText(str(data))
            self.tbNotas.setHorizontalHeaderItem(i,item)
# Llena tabla
        for i, nota in enumerate(self.listNotas.getNotas()):
            item = QTableWidgetItem(1)
            item.setText(("   %s \t") % (nota.id))
            self.tbNotas.setItem(i,0,item)
            item = QTableWidgetItem(1)
            item.setText(("   %s \t") % (nota.fecha))
            self.tbNotas.setItem(i,1,item)
            item = QTableWidgetItem(1)
            item.setText(("   %s \t") % (nota.getTotalVendido()))
            self.tbNotas.setItem(i,2,item)
            item = QTableWidgetItem(1)
            item.setText(("   %s \t") % (nota.getTotalGanancia()))
            self.tbNotas.setItem(i,3,item)
# boton eleminar
            btEliminar = QPushButton("Cancelar", None)
            #btEliminar.setIcon(icon)
            self.connect(btEliminar, SIGNAL("clicked()"), self.cancelarNota)
            self.tbNotas.setCellWidget(i,4,btEliminar)
# boton ver
            btVer = QPushButton("Ver", None)
            #btEliminar.setIcon(icon)
            self.connect(btVer, SIGNAL("clicked()"), self.verNota)
            self.tbNotas.setCellWidget(i,5,btVer)
        self.tbNotas.resizeColumnsToContents()
        textocss =  """
        <p>
        <span style="font-size:10pt; font-weight:600;">El numero de  ventas registras es de: </span>
        <span style="font-size:16pt; font-weight:600; color:#368bb2;">%s </span></p>""" % (self.listNotas.count())
        self.lbTotalVendido.setText(textocss)
        textocss = """
        <p>La suma total de ventas hasta el momento es de: <span style="font-size:xx-large; color:#368bb2;">$ %s\n </span>
        <p>La ganancia total del dia de hoy es de: <span style="font-size:xx-large; color:#368bb2;">$ %s\n </span></p>""" % (self.listNotas.getTotalVendido(), self.listNotas.getTotalGanancia())
        self.lbTotalGanancia.setText(textocss)

# elimina una nota registrada
    def cancelarNota(self):
        button = qApp.focusWidget()
        index = self.tbNotas.indexAt(button.pos())
        if index.isValid():
            ref = "%s" % self.tbNotas.item(index.row(),0).text()
            reply = QMessageBox.question(self, 'Mensaje', "desea eliminar: "+ref, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                query = "DELETE FROM notas WHERE id="+ref+";"
                #print query
                self.db.execute(query)
                self.db.commit();
                self.corte_caja()

# ver una nota registrada
    def verNota(self):
        button = qApp.focusWidget()
        index = self.tbNotas.indexAt(button.pos())
        if index.isValid():
            ref = "%s" % self.tbNotas.item(index.row(),0).text()
            sql = "select * from notas where id=%s" % (ref)
            datosNota = self.db.fetchone(sql)
            nota = Nota(self.db, datosNota)
            self.showPrint.setText(nota)
            self.showPrint.exec_()
            #self.showPrint.textEdit.print_(printer)

# elimia de la tabla de busqueda
    def delete(self):
        y = int(self.tabla.currentRow())
        ref = int(self.tabla.item(y,0).text())
        for prod in self.basket:
            if (prod[0]==ref):
                prod[4]=0
                self.basket.remove(prod)
        self.tabla.removeRow(y)
        self.grant()

    def limpiar(self):
        self.tabla.setRowCount(0)
        self.basket=[]
        self.cliente=[0,"Normal mostrador",'','','']    
        self.display()
        self.grant()
        self.tipo=0
        self.rmen.setChecked(True)
        self.desc=0
        self.nota=self.db.fetchone("select `id` from notas order by `id` desc limit 1;")
        self.nota=str(self.nota[0])
        self.lnota.setText("Ultima Nota: <b>#"+self.nota+"</b>")    
        self.codigo.setFocus()
        self.txt=""
        print "============================ Lista limpia! ============================="
    
    def imprimir(self, nota, total, recibo, cambio):
        printer = QPrinter(QPrinter.PrinterResolution)
        printer.setResolution(20)
        #printer.setFullPage(True)
        printer.setPageMargins ( .5,0,.3,0,QPrinter.Inch )
        printer.setOutputFormat(QPrinter.NativeFormat)
        #printer.setOutputFileName("nonwritable.pdf")
        #prev = QPrintPreviewDialog(printer,self)
        #prev.exec_()
        dlg = QPrintDialog(printer, self)
        if (dlg.exec_() == QDialog.Accepted):
            self.showPrint.setTextB(self.fecha, nota, self.basket, total, recibo, cambio)
            self.showPrint.exec_()
            self.showPrint.textEdit.print_(printer)

    def showInfo(self):
        info  = ShowInfo()
        info.exec_()

#primer secuencia de agregado a la canasta, aqui se recolectan los datos de la tupla temporal y se envian ingreso
    def agregar(self):
        if (self.txt!=""):
            try:
                cant = float(self.cant.text())
                importe = cant*float(self.tutmp[3])
            except ValueError:
                QMessageBox.information(self,'Aviso','Ingrese un valor numerico')
                return
            self.tutmp[1] = cant
            self.tutmp[4]= importe
            self.ingreso(self.tutmp)
            #self.tutmp=None

#despliega informacion acerca del cliente y el producto en el display de datos generales 
    def display(self):
        if (str(self.codigo.text()) !=""):
            if (str(self.codigo.text())[0].isdigit()):
                self.cant.setFocus()            
                self.txt=str(self.codigo.text())
                self.sec1(self.txt)
                self.linfo.setText(str(self.tutmp[2]))
                self.linfo2.setText(str(self.tutmp[3]))
                #self.codigo.clear()
                self.cant.setText("1")
                self.cant.selectAll()

    def setFocus1(self):
        self.tpdesc.setFocus()

    def setFocus2(self):
        self.cpdep.setFocus()

    def setFocus3(self):
        self.txtPrecio.setFocus()

    def setFocus4(self):
        self.txtPrecioPublico.setFocus()

#Secuencia 1 es la primer secuencia que busca un producto por codigo de barras o
#por referencia crea un producto temporal  y devuelve el resulado de la base de datos
    def sec1(self,txt):
        query = "SELECT `id`,`descripcion`,`precio_publico` FROM productos where `id`='%s' OR `codigo_bar`='%s' or `descripcion`='%s' order by codigo_bar limit 1" % (txt,txt,txt)
        rec = self.db.fetchone(query)
        self.tutmp=[int(rec[0]), 0,str(rec[1]), float(rec[2]),0]
        self.linfo.setText(str(rec[1]))
        self.linfo2.setText(str(rec[2]))        
        return rec

    def buscar_canasta(self,tupla):
#Busca un producto dentro de la canasta de compra y regresa verdadero si existe y falso en caso contrario
        ret=False
        if (len(self.basket)>0):
            for i,prod in enumerate(self.basket):
                if (prod[0]==tupla[0]):
                    prod[1]+=tupla[1]
                    prod[4]=prod[1]*prod[3]
                    for j,data in enumerate(prod):
                        self.tabla.item(i,j).setText(str(data))
                    ret=True
        return ret

#Hace la suma de todos los productos es un Gran Total
    def grant(self):
        suma=0
        for prod in self.basket:
            suma+=float(prod[4])
        total = suma
        desc = 0;
        self.ltotal.setText(str(suma))
        self.datos.setText("<p align=\"right\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt; font-weight:600; font-style:italic;\">Subtotal:</span><span style=\" font-size:11pt;\">     </span><span style=\" font-size:11pt; font-weight:600; \">$ "+str(suma)+"</span></p>\
<p align=\"right\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt; font-weight:600;\"><span style=\" font-style:italic;\">Descuento:    </span><span style=\" \">$ "+str(desc)+"</span></p>\
<p align=\"right\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt; font-weight:600; \"><span style=\" font-style:italic; \">Total:    </span><span style=\" font-style:italic;\">        </span>$ "+str(total)+"</p>")
        return total

    def ingreso(self,tupla):
#Se encarga de visualizar y agregar los datos de una tupla que contenga un producto su cantidad y precio
        if (self.buscar_canasta(tupla)==False):
            self.basket.append(tupla)
            self.tabla.setRowCount(len(self.basket)+1)     
            for i,data in enumerate(tupla):
                item = QTableWidgetItem(1)
                item.setText(str(data))
                self.tabla.setItem(len(self.basket)-1,i , item)
            self.tabla.resizeColumnsToContents()   
            self.grant()
            self.codigo.setFocus()
            self.codigo.selectAll()

# Almacena en la base de datos, l nota con todos sus elementos
# se almacenan los precios de los productos al momento de la venta, debido
# a que estos pueden variar
    def allocate(self, total, recibo, cambio):
        no_nota = int(self.nota)+1
        rs="INSERT INTO notas_productos(nota, id_producto, precio, precio_publico, cantidad) VALUES "
        cants=""
        ret=False;
        for aux in self.basket:
            p = self.productsList.findProduct(str(aux[0]))
            rs = rs + "(%d,%d,%f,%f,%s) ," % (no_nota, p.id, p.precio, p.precio_publico, str(aux[1]))
        try:
            query = "INSERT INTO notas(id, total, recibido, cambio, fecha) VALUES (%d,%f,%f,%f,%s);" % (no_nota,total,recibo,cambio, str(self.hoy.strftime("'20%y-%m-%d'")))
            self.db.execute(query)
            self.db.execute(rs[0:-1]+";")
            self.db.commit()
        except sqlite3.Error, e:
            print "Error %s" % (e)
            QMessageBox.critical(self, "Error!", "La nota no pudo ser registrada !!")
            ret=False
        else:
            ret=True

    def gencode(self):
        #codigo=str(self.tpcodigo.text())
        codigo = str(random.randrange(10000))
        suma=''
        for car in codigo:
            suma+=str(ord(car))
        self.tpcodigo.setText(str(suma))

# agrega un nuevo producto
    def add_producto(self):
        msgInfo = "El producto ha sido dado de alta.\n su referencia es "
        msgWarning = "No se ha podido ingresar. Verifique los datos"
        msgVauelError = "Los precios deben ser valores numericos"
        try:
            precio = float(str(self.txtPrecio.text()))
            precio_publico = float(str(self.txtPrecioPublico.text()))
        except ValueError:
            QMessageBox.information(self, "Registrado", msgVauelError)
            return
        query =  """insert into productos(codigo_bar, descripcion, seccion, precio, precio_publico) 
                    values (%s,'%s','%s',%s,%s)""" % (str(self.tpcodigo.text()), str(self.tpdesc.text()).upper().strip(), 
                    str(self.cpdep.currentText()),precio, precio_publico)
        try:
            self.db.execute(query)
            self.db.commit();
        except sqlite3.Error, e:
            print "Error %s" % (e)
            QMessageBox.critical(self, "Error!", msgWarning)
        else:
            sql = "SELECT `id` from productos where codigo_bar="+str(self.tpcodigo.text())
            pd = self.db.fetchone(sql)
            QMessageBox.information(self, "Registrado", msgInfo+str(pd[0]))
        self.tpcodigo.setText('')
        self.tpdesc.setText('')
        self.txtPrecio.setText('')
        self.txtPrecioPublico.setText('')

if __name__=="__main__":
    app = QApplication(sys.argv)
    pic = QPixmap(":./images/splash.png")
    splash = QSplashScreen(pic)
    app.processEvents()
    splash.showMessage("Loaded modules")
    #splash.setMask(pic.mask())
    splash.show()
    aw = ingreso()
    aw.show()
    sys.exit(app.exec_())

