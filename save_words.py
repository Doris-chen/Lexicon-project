# save_words.py

import pymysql
import re

# 打开文件dict.txt
f = open("dict.txt")

# 创建数据库连接
db = pymysql.connect(host="localhost", user="root",
                     passwd="123456", db="lexicon",
                     charset="utf8")

# 利用db创建游标对象
cursor = db.cursor()

# 提取数据
for line in f:
    try:
        l = re.split(r"\s+", line)
        word = l[0]
        interpret = ' '.join(l[1:])
    except:
        pass

    # 利用cursor的execute()方法执行SQL语句
    sql_insert = "insert into words(word,interpret) values(%s,%s)"
    L = [word, interpret]
    try:
        cursor.execute(sql_insert, L)

        # 提交到数据库执行
        db.commit()
    except:
        db.rollback()

# 关闭文件
f.close()










