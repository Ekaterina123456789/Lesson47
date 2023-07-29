import sqlite3
import time
import re

from flask import url_for


class DataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def get_objects(self, table):
        sql = f"SELECT * FROM {table}"
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except IOError:
            print('Ошибка чтения базы данных')
        return []

    def add_post(self, title, text, url):
        try:
            self.__cur.execute(f'SELECT COUNT() as "count" FROM posts WHERE url LIKE "{url}"')
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print('Отзыв с таким url уже существует!')
                return False

            base = url_for('static', filename='images')
            text = re.sub(r'(?P<tag><img\s+[^>]*scr=)(?P<quote>[\'"])(?P<url>.*)(?P=quote)>', r'\g<tag>' + base + r'/\g<url>>', text)
            tm = int(time.time())
            sql = f'INSERT INTO posts VALUES(NULL, ?, ?, ?, ?)'
            self.__cur.execute(sql, (title, text, url, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка добавления статьи в базу данных' + str(e))
            return False
        return True

    def get_post(self, post_id):
        try:
            self.__cur.execute(f'SELECT title, text FROM posts WHERE url == "{post_id}"')
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print('Ошибка получения статьи из базы данных', str(e))
        return None, None

    def add_product(self, title, photo, price):
        try:
            self.__cur.execute(f'SELECT COUNT() as "count" FROM products WHERE title LIKE "{title}"')
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print('Такой товар уже существует!')
                return False

            base = url_for('static', filename='images')
            photo = re.sub(r'(?P<tag><img\s+[^>]*scr=)(?P<quote>[\'"])(?P<url>.*)(?P=quote)>', r'\g<tag>' + base + r'/\g<url>>', photo)
            sql = f'INSERT INTO products VALUES(NULL, ?, ?, ?)'
            self.__cur.execute(sql, (title, photo, price))
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка добавления товара в базу данных' + str(e))
            return False
        return True

    def get_product(self, product_id):
        try:
            self.__cur.execute(f'SELECT title, photo, price FROM products WHERE id == "{product_id}"')
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print('Ошибка получения товара из базы данных', str(e))
        return None, None
