from flask import Flask, render_template, request, redirect, url_for, session, flash
from cryptography.fernet import Fernet
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'cyber_security_key_2026' # مفتاح لتأمين الجلسة

# وظيفة لإدارة مفتاح التشفير
def get_key():
    if not os.path.exists("secret.key"):
        key = Fernet.generate_key()
        with open("secret.key", "wb") as k: k.write(key)
    return open("secret.key", "rb").read()

cipher = Fernet(get_key())

# إعداد قاعدة البيانات
def init_db():
    with sqlite3.connect('database.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS accounts 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      site TEXT, user TEXT, password BLOB)''')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # كلمة المرور الرئيسية للدخول للموقع
        if request.form['master_pass'] == 'Admin123': 
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        flash('كلمة المرور الرئيسية خاطئة!')
    return render_template('login.html')

@app.route('/')
def dashboard():
    if not session.get('logged_in'): return redirect(url_for('login'))
    with sqlite3.connect('database.db') as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute('SELECT * FROM accounts').fetchall()
    data = []
    for r in rows:
        dec_pass = cipher.decrypt(r['password']).decode()
        data.append({'id':r['id'], 'site':r['site'], 'user':r['user'], 'pass':dec_pass})
    return render_template('dashboard.html', accounts=data)

@app.route('/add', methods=['POST'])
def add():
    if not session.get('logged_in'): return redirect(url_for('login'))
    site, user, pswd = request.form['site'], request.form['user'], request.form['pass']
    enc_pass = cipher.encrypt(pswd.encode())
    with sqlite3.connect('database.db') as conn:
        conn.execute('INSERT INTO accounts (site, user, password) VALUES (?,?,?)', (site, user, enc_pass))
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    # تشغيل الموقع على المنفذ 80 ليعمل الدومين مباشرة
    app.run(host='0.0.0.0', port=80, debug=True)