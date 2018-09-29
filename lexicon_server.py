# lexicon_server.py
# !/bin/user/env python3
# coding = utf-8

'''
name: Doris
date: 2018-9-28
email: 1102498089@qq.com
modules: python3.5 mysql pymysql
This is a dict project
'''

from socket import *
import pymysql
import os
import sys
import time
import signal

# 定义需要的全局变量
DICT_TEXT = "./dict.txt"
HOST = "0.0.0.0"
PORT = 8000
ADDR = (HOST, PORT)


# 流程控制
def main():
    # 创建数据库连接
    db = pymysql.connect(host="localhost", user="root",
                         passwd="123456", db="lexicon",
                         charset="utf8")

    # 创建流式套接字
    s = socket()
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(ADDR)
    s.listen(5)

    # 忽略子进程信号
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    while True:
        try:
            c, addr = s.accept()
            print("Connect from", addr)
        except KeyboardInterrupt:
            s.close()
            sys.exit("服务器退出")
        except Exception as e:
            print(e)
            continue

        # 创建子进程处理客户端请求
        pid = os.fork()
        if pid == 0:
            s.close()
            do_chid(c, db)
        else:
            c.close()
            continue


def do_chid(c, db):
    # 循环接收请求
    while True:
        data = c.recv(1024).decode()
        print("Request: ", data)

        if (not data) or data[0] == 'E':
            c.close()
            sys.exit(0)
        elif data[0] == 'R':
            do_register(c, db, data)
        elif data[0] == 'L':
            do_login(c, db, data)
        elif data[0] == 'Q':
            do_query(c, db, data)
        elif data[0] == 'H':
            do_history(c, db, data)


def do_register(c, db, data):
    print("注册操作")
    L = data.split(' ')
    name = L[1]
    password = L[2]

    cursor = db.cursor()
    sql_select = "select * from user where name='%s'" % name
    cursor.execute(sql_select)
    r = cursor.fetchone()

    if r is not None:
        c.send(b"EXISTS")
        return

    # 用户不存在，则向数据库插入用户
    sql_insert = "insert into user(name,password) \
                  values('%s','%s')" % (name, password)
    try:
        cursor.execute(sql_insert)
        db.commit()
        c.send(b"OK")
    except:
        db.rollback()
        c.send(b"FAIL")
        return
    else:
        print("%s注册成功" % name)


def do_login(c, db, data):
    print("登录操作")
    L = data.split(' ')
    name = L[1]
    password = L[2]

    cursor = db.cursor()
    sql_select = "select * from user where name='%s' and \
           password='%s'" % (name, password)
    cursor.execute(sql_select)
    r = cursor.fetchone()

    if r is None:
        c.send("用户名或密码不正确".encode())
    else:
        print("%s登录成功" % name)
        c.send(b"OK")


def do_query(c, db, data):
    print("查询操作")
    L = data.split(' ')
    name = L[1]
    word = L[2]
    cursor = db.cursor()

    def insert_history():
        tm = time.ctime()
        sql_insert = "insert into history(name,word,time) \
                      value('%s','%s','%s')" % (name, word, tm)
        try:
            cursor.execute(sql_insert)
            db.commit()
        except:
            db.rollback()
            return

    # 文本查询
    try:
        f = open(DICT_TEXT)
    except:
        c.send(b"FAIL")
        return
    for line in f:
        tmp = line.split(' ')[0]
        if tmp > word:
            c.send("没有查询到该单词".encode())
            f.close()
            return
        elif tmp == word:
            c.send(b"OK")
            time.sleep(0.1)
            c.send(line.encode())
            f.close()
            insert_history()
            return
    c.send(b"FAIL")
    f.close()


def do_history(c, db, data):
    print("历史记录")
    name = data.split(' ')[1]
    cursor = db.cursor()

    sql_select = "select * from history where name='%s'" % name
    cursor.execute(sql_select)
    r = cursor.fetchall()
    if not r:
        c.send("没有历史记录".encode())
        return
    else:
        c.send(b"OK")

    for i in r:
        time.sleep(0.1)
        msg = "%s    %s    %s" % (i[1], i[2], i[3])
        c.send(msg.encode())
    time.sleep(0.1)
    c.send(b"##")


if __name__ == "__main__":
    main()



