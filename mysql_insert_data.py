#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: zhoubin
# Date: 2019/6/4
# Description: 该工具主要用于对MySQL数据库进行压力测试

import string
import argparse
import random
import threading
import time
import pymysql

from contextlib import contextmanager

DB_NAME = 'test_insert_data_db'
TABLE_NAME = 'test_insert_data_table'
CREATE_TABLE_STATEMENT = """CREATE TABLE {0} (id INT(10) NOT NULL PRIMARY KEY AUTO_INCREMENT,
                                              name VARCHAR(255) NOT NULL,
                                              datetime DOUBLE NOT NULL)""".format(TABLE_NAME)


def _argparse():
    """ 命令行参数解析 """
    parser = argparse.ArgumentParser(description='benchmark tool for MySQL database')
    parser.add_argument('--host', action='store', dest='host',
                        required=True, help='connect to host')
    parser.add_argument('--user', action='store', dest='user',
                        required=True, help='user for login')
    parser.add_argument('--password', action='store', dest='password',
                        required=True, help='password to use when connecting ')
    parser.add_argument('--port', action='store', dest='port', default=3306, type=int,
                        help='port number to use for connection or 3306 for default')
    parser.add_argument('--thread_size', action='store', dest='thread_size',
                        default=5, type=int, help='how much connection for database usage')
    parser.add_argument('--row_size', action='store', dest='row_size', default=5000, type=int,
                        help='how much rows')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1')
    return parser.parse_args()


@contextmanager
def get_conn(**kwargs):
    """ 获取 Connection 对象 """
    conn = pymysql.connect(**kwargs)
    try:
        yield conn
    finally:
        conn.close()


def create_db_and_table(conn):
    """ 创建数据库与表 """
    with conn as cur:
        for sql in ["DROP DATABASE IF EXISTS {0}".format(DB_NAME),
                    "CREATE DATABASE {0}".format(DB_NAME),
                    "USE {0}".format(DB_NAME),
                    CREATE_TABLE_STATEMENT]:
            print(sql)
            cur.execute(sql)


def random_string(length=10):
    """ 生成长度为 10 的随机字符串 """
    s = string.ascii_letters + string.digits
    return ''.join(random.sample(s, length))


def add_row(cursor):
    """ 执行插入语句 """
    SQL_FORMAT = "INSERT INTO {0}(name, datetime) VALUES('{1}', {2})"
    sql = SQL_FORMAT.format(TABLE_NAME, random_string(), time.time())
    cursor.execute(sql)


def insert_data(conn_args, row_size):
    """ 插入数据到数据库 """
    with get_conn(**conn_args) as conn:
        with conn as c:
            c.execute('use {0}'.format(DB_NAME))
        with conn as c:
            for i in range(row_size):
                add_row(c)
                conn.commit()


def main():
    parser = _argparse()
    conn_args = dict(host=parser.host, user=parser.user, password=parser.password, port=parser.port)
    with get_conn(**conn_args) as conn:
        create_db_and_table(conn)

    threads = []
    for i in range(parser.thread_size):
        t = threading.Thread(target=insert_data, args=(conn_args, parser.row_size))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()


if __name__ == '__main__':
    main()
