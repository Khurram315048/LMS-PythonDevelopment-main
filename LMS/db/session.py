
import pymysql
from pymysql.cursors import DictCursor
from core.config import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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

engine=create_engine("mysql+pymysql://",creator=mysql.get_connection,pool_pre_ping=True)
SessionLocal=sessionmaker(bind=engine)




