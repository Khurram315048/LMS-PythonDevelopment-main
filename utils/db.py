# from flask_mysqldb import MySQL

# mysql = MySQL()


import pymysql
from pymysql.cursors import DictCursor
from config import *

class Database:
    def __init__(self):
        self.host=MYSQL_HOST
        self.user=MYSQL_USER
        self.password=MYSQL_PASSWORD
        self.database=MYSQL_DB
        self.port=MYSQL_PORT


    def get_connection(self):
        return pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            port=self.port,
            autocommit=True
        )   


    def get_dict_connection(self):
        return pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            port=self.port,
            cursorclass=DictCursor,
            autocommit=True
        ) 


mysql=Database()    