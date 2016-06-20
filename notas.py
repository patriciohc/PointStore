#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# nota
import dataBase
from productsList import ProductsList

class ListaNotas():

    def __init__(self, dataB):
        self.db = dataB
        self.numero = 0

# regresa una nota en base a la fecha recibida
    def findNotas(self, fechaIni, fechaFin = ""):
        if fechaFin == "":
            sql = "select * from notas where fecha = '%s' " %(fechaIni)
        else:
            sql = "select * from notas where fecha >= '%s' and fecha <= '%s' " %(fechaIni,fechaFin)
        result = self.db.fetchall(sql)
        self.notas = []
        self.numero = 0
        for nota in result:
            self.numero += 1
            self.notas.append(Nota(self.db, nota))
        self.calcTotal()

    def calcTotal(self):
        self.total = 0
        self.ganancia = 0
        for nota in self.notas:
            self.total += nota.getTotalVendido()
            self.ganancia += nota.getTotalGanancia()

    def getTotalVendido(self):
        return self.total

    def getTotalGanancia(self):
        return self.ganancia

    def getNotas(self):
        return self.notas

    def count(self):
        return self.numero

    def getNotas(self):
        return self.notas


class Nota():

    def __init__(self, dataBase, atrs):
        self.db =  dataBase
        self.id = atrs[0]
        self.recibido = atrs[2]
        self.cambio = atrs[3]
        self.fecha = atrs[4]
        self.getProductos()
        self.calcTotal()

    def getProductos(self):
        sql = "select * from  notas_productos where nota = %s;" % (self.id)
        result = self.db.fetchall(sql)
        self.productos = []
        for producto in result:
            self.productos.append(ProductoNota(self.db, producto))

    def calcTotal(self):
        self.total = 0.0
        self.ganancia = 0.0
        for p in self.productos:
            self.total += p.getTotalVendido()
            self.ganancia += p.getTotalGanancia()

    def getTotalVendido(self):
        return self.total

    def getTotalGanancia(self):
        return self.ganancia



class ProductoNota():

    def __init__(self, dataBase, atrs):
        self.id = atrs[0]
        self.producto = self.getProducto(dataBase,atrs[2])
        self.precio = float(atrs[3])
        self.precio_publico = float(atrs[4])
        self.cantidad = float(atrs[5])

    def getProducto(self, dataBase,idp):
        plist = ProductsList(dataBase)
        return plist.findProduct(idp)

    def getTotalVendido(self):
        return self.precio_publico * self.cantidad

    def getTotalGanancia(self):
        return self.precio_publico * self.cantidad - self.precio * self.cantidad


