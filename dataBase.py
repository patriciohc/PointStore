#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sqlite3, ConfigParser  

class dataBase():
    def __init__(self):
        pass

    def connect(self):
        cfg = ConfigParser.ConfigParser()
        cfg.read(["./config.cfg"])
        #cfg.read(["./config.cfg"])
        if cfg.has_option("sqlite", "host"):  
            data = cfg.get("sqlite", "db")
        else:
            print ("No se encontro el nombre en el archivo de configuracion.")
            return False  
        try:
            self.db = sqlite3.connect(data)
        except sqlite3.Error, e:
            print "error al conectar con base de datos: " + e
            return False
        else:           
            self.cursor = self.db.cursor()
            return True     


    def fetchall(self, query):
        print query
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def fetchone(self, query):
        print query
        self.cursor.execute(query)
        return self.cursor.fetchone()

    def execute(self, query):
        print query
        self.cursor.execute(query)

    def commit(self):
        self.db.commit()



