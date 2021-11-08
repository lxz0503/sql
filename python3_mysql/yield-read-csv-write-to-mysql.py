"""
This can read data from other file like txt or csv, and write data into mysql database.
It also supports other database functions like select,insert alter and update records.
"""
# !/usr/bin/python3
# coding=utf-8
import pymysql
from operations import *
import csv
from collections import namedtuple
import configparser


class DatabaseInit(object):
    def __init__(self, sql_conf):
        self.charset = 'utf8'
        self.host, self.port, self.db_name, self.user, self.password = self.__get_sql_config()
        self.sql_conf = sql_conf
        self.conn = None
        self.cur = None

    def __get_sql_config(self):
        cf = configparser.ConfigParser()
        cf.read(self.sql_conf)
        host = cf.get("mysqlconf", "host")
        port = cf.get("mysqlconf", "port")
        db = cf.get("mysqlconf", "db_name")
        user = cf.get("mysqlconf", "user")
        password = cf.get("mysqlconf", "password")
        return host, port, db, user, password

    def connect_db(self):                # this is to connect database system
        try:
            conn = pymysql.Connect(
                                   host=self.host,
                                   user=self.username,
                                   passwd=self.password,
                                   # db = self.dbname,    # this is only used when you already have a database
                                   charset=self.charset
                                  )
            cur = conn.cursor()
        except Exception as e:
            print("connect error", e)
        else:
            self.conn = conn
            self.cur = cur

    def disconnect_db(self):
        self.cur.close()
        self.conn.close()

    def create(self):           # this is for specific operations like creating database and table
        try:
            self.connect_db()
            self.cur.execute(drop_database)
            self.cur.execute(create_database)   # create database
            self.conn.select_db('test_result')  # connect your database
            # self.cur.execute(drop_table)
            self.cur.execute(create_table)      # create table
        except Exception as e:
            print("create error", e)
        else:
            self.conn.commit()    # do not forget to commit after modification
            self.disconnect_db()
            print('create database and table ok')

    @staticmethod
    def get_data(file_name):          # read data from csv file
        with open(file_name) as f:
            f_csv = csv.reader(f)
            headings = next(f_csv)    # use iterator
            Row = namedtuple('Row', headings)    # this is a trick??? xiaozhan
            for r in f_csv:
                yield Row(*r)     # r is a list

    def insert(self, insert_data, args):
        try:
            self.connect_db()
            self.cur.execute('use test_result')
            # self.conn.select_db('test_result')   # same with above line
            # self.cur.execute(insert_data)
            self.cur.executemany(insert_data, args)   # this is ok,
        except Exception as e:
            self.conn.rollback()
            print('insert error:', e)
        else:
            self.conn.commit()          # do not forget to commit after modification
            self.disconnect_db()

    def search_data(self):
        try:
            self.connect_db()
            self.cur.execute('use test_result')
            # self.cur.execute('select * from ia_result')   # you can set parameters as below line
            self.cur.execute(select_data, select_args)
            res = self.cur.fetchall()
        except Exception as e:
            print(e)
        else:
            self.disconnect_db()
            # print('Failed cases are:')
            fail_dict = {}
            for row in res:
                print(row)
                if row[2] == 'FAIL':
                    fail_dict.setdefault(row[1], row[2])
            return fail_dict

    def update_data(self):
        try:
            self.connect_db()
            self.cur.execute('use test_result')
            self.cur.execute(update_data, update_args)
        except Exception as e:
            self.conn.rollback()
            print('update error:', e)
        else:
            self.conn.commit()    # do not forget to commit after modification
            self.disconnect_db()

    def alter_table(self):
        try:
            self.connect_db()
            self.cur.execute('use test_result')
            self.cur.execute(alter_table)
        except Exception as e:
            self.conn.rollback()
            print('alter error:', e)
        else:
            self.conn.commit()    # do not forget to commit after modification
            self.disconnect_db()


if __name__ == '__main__':
    db = DatabaseInit('db_config.ini')      # 家里的win7只能用gbk编码,utf8 is for company
    db.connect_db()
    db.create()
    # xiaozhan debug, auto generate id.
    for i, t in enumerate(db.get_data('data.csv'), 1):      # the table index always starts from 1
        args = [(t.name, t.status, t.arch, t.sprint)]      # this is to generate parameter for excecutemany
        db.insert(insert_data, args)    # insert_data is at operations.py
    # xiaozhan debug end
    # this can put failed cases into a dictionary
    # res = db.search_data()
    # print(res)
    # # after rerun, you need to update test result again
    # db.alter_table()   # add date column
    # db.update_data()
    # time.sleep(5)
    # res = db.search_data()  # tuple change to a list
    # if len(res) != 0:
    #     print('modify not ok, check log')









