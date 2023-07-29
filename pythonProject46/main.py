import sqlite3
import os

from flask import Flask, render_template, request, flash, url_for, abort, session, redirect

from DataBase import DataBase

DATABASE = '/tmp/evrol.db'
DEBUG = True
SECRET_KEY = '777jhgkjfhhjgjhgjhgfhgfdkgjhfj765'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update({'DATABASE': os.path.join(app.root_path, 'evrol.db')})


def connect_db():
    con = sqlite3.connect(app.config['DATABASE'])
    con.row_factory = sqlite3.Row
    return con


def create_db():
    db = connect_db()
    with open('create_db.sql', 'r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


app.config['SECRET_KEY'] = '777jhgkjfhhjgjhgjhgfhgfdkgjhfj765'

# menu = [{'name': 'Главная', 'url': 'index'},
#         {'name': 'О нашей продукции', 'url': 'about'},
#         {'name': 'Каталог', 'url': 'catalog'},
#         {'name': 'Обратная связь', 'url': 'contacts'}]
#
# catalog_menu = [{'c_name': 'Масло для легковых автомобилей', 'c_url': 'maslodlyalegkovihavto'},
#                 {'c_name': 'Масло для 4-х тактных двигателей', 'c_url': 'maslodlya2taktnih'},
#                 {'c_name': 'Масло для 2-х тактных двигателей', 'c_url': 'maslodlya4taktnih'},
#                 {'c_name': 'Масло для грузовых автомобилей', 'c_url': 'maslodlyagruzovihavto'}]


@app.route('/index')
@app.route('/')
def index():
    db_con = connect_db()
    dbase = DataBase(db_con)
    return render_template('index.html', title='Главная',
                           menu=dbase.get_objects('mainmenu'),
                           posts=dbase.get_objects('posts'))


@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    db_con = connect_db()
    dbase = DataBase(db_con)
    if request.method == 'POST':
        if len(request.form['title']) < 3 or len(request.form['text']) < 10:
            flash('Ошибка добавления отзыва', category='error')
        else:
            res = dbase.add_post(request.form['title'], request.form['text'], request.form['url'])
            if res:
                flash('Отзыв успешно добавлен!', category='success')
            else:
                flash('Ошибка добавления отзыва', category='error')
    return render_template('add_post.html', title='Добавить отзыв', menu=dbase.get_objects('mainmenu'))


@app.route('/post/<post_id>')
def show_post(post_id):
    db_con = connect_db()
    dbase = DataBase(db_con)

    title, post = dbase.get_post(post_id)
    if not title:
        abort(404)

    return render_template('post.html', title=title, post=post, menu=dbase.get_objects('mainmenu'))


@app.route('/about')
def about():
    db_con = connect_db()
    dbase = DataBase(db_con)
    return render_template('about.html', title='О нашей продукции', menu=dbase.get_objects('mainmenu'))


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    db_con = connect_db()
    dbase = DataBase(db_con)
    if request.method == 'POST':
        res = dbase.add_product(request.form['title'], request.form['photo'], request.form['price'])
        if res:
            flash('Товар успешно добавлен!', category='success')
        else:
            flash('Ошибка добавления товара!', category='error')
    return render_template('add_product.html', title='Добавить товар', menu=dbase.get_objects('mainmenu'))


@app.route('/product/<product_id>')
def show_product(product_id):
    db_con = connect_db()
    dbase = DataBase(db_con)

    title, photo, price = dbase.get_product(product_id)
    if not title:
        abort(404)

    return render_template('product.html', title=title, photo=photo, price=price, menu=dbase.get_objects('mainmenu'), products=dbase.get_objects('products'))


@app.route('/catalog')
def catalog():
    db_con = connect_db()
    dbase = DataBase(db_con)
    return render_template('catalog.html', title='Каталог', menu=dbase.get_objects('mainmenu'), products=dbase.get_objects('products'))


@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    db_con = connect_db()
    dbase = DataBase(db_con)
    if request.method == 'POST':
        if len(request.form['username']) > 1:
            flash('Сообщение отправлено успешно', category='success')
        else:
            flash('Ошибка отправки!', category='error')
        print(request.form)
        context = {
            'username': request.form['username'],
            'email': request.form['email'],
            'message': request.form['message']
        }
        return render_template('contacts.html', title='Обратная связь', menu=dbase.get_objects('mainmenu'), **context)
    return render_template('contacts.html', title='Обратная связь', menu=dbase.get_objects('mainmenu'))


@app.route('/profile/<username>')
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return f'Пользователь {username}'


@app.route('/login', methods=['GET', 'POST'])
def login():
    db_con = connect_db()
    dbase = DataBase(db_con)
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST' and request.form['username'] == 'admin'\
            and request.form['password'] == 'qwerty':
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogged']))
    return render_template('login.html', title='Авторизация', menu=dbase.get_objects('mainmenu'))


@app.errorhandler(404)
def page_not_found(error):
    db = connect_db()
    dbase = DataBase(db)
    return render_template('page404.html', title='Страница не найдена', menu=dbase.get_objects('mainmenu'))


if __name__ == '__main__':
    create_db()
    app.run()
