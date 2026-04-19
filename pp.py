from flask import Flask, render_template, render_template_string, request, session, redirect
import sqlite3 as sq
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "my_secret_key_123"

# ================= SECURITY =================
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'


# ================= DATABASE =================
def connect_db():
    return sq.connect('users.db')


def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()


create_table()


# ================= HTML =================
HTML = open('index.html', encoding='utf-8').read()


# ================= HOME =================
@app.route('/', methods=['GET', 'POST'])
def home():

    # لو المستخدم مسجل دخول يروح مباشرة
    if 'user' in session:
        return redirect('/home')

    login_msg = ""
    signup_msg = ""
    login_type = ""
    signup_type = ""
    view = "login"

    conn = connect_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        action = request.form.get('action')

        # ================= LOGIN =================
        if action == 'login':
            email = request.form['username_login']
            password = request.form['password_login']

            cursor.execute(
                'SELECT password FROM users WHERE email = ?',
                (email,)
            )
            user = cursor.fetchone()

            if not user or not check_password_hash(user[0], password):
                login_msg = "بيانات الدخول غير صحيحة"
                login_type = "error"
            else:
                session['user'] = email
                conn.close()
                return redirect('/home')

        # ================= SIGNUP =================
        elif action == 'signup':
            view = "signup"

            first_name = request.form['firstname_signup']
            last_name = request.form['lastname_signup']
            email = request.form['signup_email']
            password_signup = request.form['password_signup']
            confirm_password = request.form['password_confirm']

            if password_signup != confirm_password:
                signup_msg = "كلمة المرور غير متطابقة"
                signup_type = "error"
            else:
                try:
                    hashed_password = generate_password_hash(password_signup)

                    cursor.execute('''
                        INSERT INTO users (first_name, last_name, email, password)
                        VALUES (?, ?, ?, ?)
                    ''', (first_name, last_name, email, hashed_password))

                    conn.commit()
                    conn.close()

                    # ❌ مهم: مفيش تحويل بعد signup
                    signup_msg = "تم إنشاء الحساب بنجاح 👌 سجل دخولك الآن"
                    signup_type = "success"

                except sq.IntegrityError:
                    signup_msg = "لا يمكن إنشاء الحساب بهذه البيانات"
                    signup_type = "error"

    conn.close()

    return render_template_string(
        HTML,
        login_msg=login_msg,
        signup_msg=signup_msg,
        login_type=login_type,
        signup_type=signup_type,
        view=view
    )


# ================= DASHBOARD =================
@app.route('/home')
def dashboard():
    if 'user' not in session:
        return redirect('/')

    return render_template('page2.html', user=session['user'])




@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/account')
def about():
    return render_template('account.html')

# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')
# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
