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
        self.max_retries=3


    def get_connection(self):
        try:
            return pymysql.connect(host=self.host,user=self.user,password=self.password,database=self.database,
                                port=self.port,autocommit=False,connect_timeout=10,read_timeout=30,write_timeout=30)   
        except pymysql.MySQLError as e:
            print(f"Error during get connection: {str(e)}")
            raise


    def get_dict_connection(self):
        try:
            return pymysql.connect(host=self.host,user=self.user,password=self.password,database=self.database,
                                    port=self.port,cursorclass=DictCursor,autocommit=False,read_timeout=30,write_timeout=30,connect_timeout=10)
        except pymysql.MySQLError as e:
            print(f"Error during get dict connection: {str(e)}")
            raise 


mysql=Database()    




# from sqlalchemy import create_engine
# from sqlalchemy.engine import URL
# from sqlalchemy.orm import declarative_base,sessionmaker
 
# from config import MYSQL_HOST,MYSQL_USER,MYSQL_PASSWORD,MYSQL_DB,MYSQL_PORT

# DATABASE_URL=URL.create(
#     drivername="mysql+pymysql",
#     username=MYSQL_USER,
#     password=MYSQL_PASSWORD,
#     host=MYSQL_HOST,
#     port=int(MYSQL_PORT),
#     database=MYSQL_DB,
#     query={
#         "charset":"utf8mb4"
#     },
# )

# engine=create_engine(
#     DATABASE_URL,
#     pool_pre_ping=True,
#     pool_recycle=280,
#     pool_size=10,
#     max_overflow=20,
#     connect_args={
#         "connect_timeout":10,
#         "read_timeout":30,
#         "write_timeout":30
#     },
# )

# SessionLocal=sessionmaker(bind=engine,autocommit=False,autoflush=False)

# Base=declarative_base()

# def get_db():
#     db=SessionLocal
#     try:
#         yield db
#     finally:
#         db.close()    