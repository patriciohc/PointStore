#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import dataBase
class ProductsList():

    def __init__(self, dataBase):
        self.db = dataBase

# regresa un producto en vase a un parametro
# descripcion, codigo de barras o id del producto
    def findProducts(self, parameter):
        sql = "SELECT * FROM productos where descripcion like '%"+txt+"%' or codigo_bar='"+txt+"' or id='"+txt+"' limit 20"
        result = self.db.fetchall(sql)
        products = []
        for elem in result:
            products.append(Product(elem))

    def findProduct(self, id):
        sql = "SELECT * FROM productos WHERE id=%s" % (id)
        result = self.db.fetchone(sql)
        return Product(result)


class Product():
    def __init__(self, atrs):
        self.id = atrs[0]
        self.codigo_bar = atrs[1]
        self.descripcion = atrs[2]
        self.seccion = atrs[3]
        self.precio = atrs[4]
        self.precio_publico = atrs[5]

