# lexicon_client.py

# !/bin/user/env python3
# coding = utf-8

from socket import *
import sys
import getpass


# 创建网络连接
def main():
    if len(sys.argv) < 3:
        print("argv is error")
        return
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    ADDR = (HOST, PORT)
    s = socket()

    try:
        s.connect(ADDR)
    except Exception as e:
        print(e)
        return

    # 进入一级界面
    while True:
        print('''
              ============Welcome=============
              --  1.注册   2.登录   3.退出  --
              ================================''')

        try:
            cmd = int(input("输入选项>>"))
        except Exception:
            print("输入命令错误")
            continue

        if cmd not in [1, 2, 3]:
            print("对不起没有该选项")
            # 清除标准输入
            sys.stdin.flush()
            continue
        elif cmd == 1:
            name = do_register(s)
            if name:
                print("注册成功")
                login(s, name)
            elif name == 1:
                print("用户已存在")
            else:
                print("注册失败")
        elif cmd == 2:
            name = do_login(s)
            if name:
                print("登录成功")
                login(s, name)
            else:
                print("登录失败")
        elif cmd == 3:
            s.send(b"E")
            sys.exit("谢谢使用")


def do_register(s):
    while True:
        name = input("用户名：")
        password = getpass.getpass("密码：")
        password2 = getpass.getpass("确认密码：")

        if (' ' in name) or (' ' in password):
            print("用户名和密码不允许有空格")
            continue

        if password != password2:
            print("两次密码不一致")
            continue

        msg = "R {} {}".format(name, password)
        # 发送请求
        s.send(msg.encode())
        # 接收回复
        data = s.recv(1024).decode()

        if data == "OK":
            return name
        elif data == 'EXISTS':
            return 1
        else:
            return 2


def do_login(s):
    name = input("用户名：")
    password = getpass.getpass("密码：")
    msg = "L {} {}".format(name, password)
    # 发送请求
    s.send(msg.encode())
    # 接收回复
    data = s.recv(1024).decode()

    if data == "OK":
        return name
    else:
        return


def login(s, name):
    while True:
        print('''
              ============Welcome=============
              -- 1.查词  2.历史记录  3.退出 --
              ================================''')

        try:
            cmd = int(input("输入选项>>"))
        except Exception:
            print("输入命令错误")
            continue

        if cmd not in [1, 2, 3]:
            print("对不起没有该选项")
            # 清除标准输入
            sys.stdin.flush()
            continue
        elif cmd == 1:
            do_query(s, name)
        elif cmd == 2:
            do_history(s, name)
        elif cmd == 3:
            return


def do_query(s, name):
    while True:
        word = input("单词：")
        if word == "##":
            break
        msg = "Q {} {}".format(name, word)
        s.send(msg.encode())
        data = s.recv(1024).decode()
        if data == "OK":
            interpret = s.recv(2048).decode()
            print(interpret)
        else:
            print("没有查到该单词")
            print()


def do_history(s, name):
    msg = "H {}".format(name)
    s.send(msg.encode())
    data = s.recv(1024).decode()

    if data == "OK":
        print("name      word      time")
        while True:
            history_data = s.recv(1024).decode()
            if history_data == "##":
                break
            print(history_data)
    else:
        print("没有历史记录")


if __name__ == "__main__":
    main()


