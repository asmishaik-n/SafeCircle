from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "safecircle_secret"
contacts = []
current_location = ""


def init_db():

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contacts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        name TEXT,
        phone TEXT
    )
''')

    conn.commit()
    conn.close()


init_db()


@app.route('/')
def home():
    return render_template("index.html")
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )

            conn.commit()

            return redirect('/login')

        except:
            return "Username already exists!"

        finally:
            conn.close()

    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:
            session['user'] = username
            return redirect('/')

        else:
            return "Invalid Username or Password"

    return render_template('login.html')
@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/login')
@app.route('/save_location', methods=['POST'])
def save_location():

    global current_location

    current_location = request.form['location']

    return "Location Saved"
@app.route('/contacts', methods=['GET', 'POST'])
def contacts_page():


    if 'user' not in session:
        return redirect('/login')

    global contacts

    message = ""

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name, phone FROM contacts WHERE username=?",
        (session['user'],)
    )

    rows = cursor.fetchall()

    contacts = []

    for row in rows:
        contacts.append({
            'name': row[0],
            'phone': row[1]
        })

    if request.method == 'POST':

        if len(contacts) >= 5:

            message = "Maximum 5 trusted contacts allowed!"

        else:

            name = request.form['name']
            phone = request.form['phone']

            cursor.execute(
                "INSERT INTO contacts (username, name, phone) VALUES (?, ?, ?)",
                (session['user'], name, phone)
            )

            conn.commit()

            message = "Contact Saved Successfully!"

            cursor.execute(
                "SELECT name, phone FROM contacts WHERE username=?",
                (session['user'],)
            )

            rows = cursor.fetchall()

            contacts = []

            for row in rows:
                contacts.append({
                    'name': row[0],
                    'phone': row[1]
                })

    conn.close()

    return render_template(
        "contacts.html",
        contacts=contacts,
        count=len(contacts),
        message=message,
        location=current_location
)
@app.route('/profile')
def profile():

    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM contacts WHERE username=?",
        (session['user'],)
    )

    count = cursor.fetchone()[0]

    conn.close()

    return render_template(
        'profile.html',
        username=session['user'],
        count=count
    )
@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/delete/<int:index>')
def delete_contact(index):

    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM contacts WHERE username=?",
        (session['user'],)
    )

    rows = cursor.fetchall()

    if index < len(rows):

        contact_id = rows[index][0]

        cursor.execute(
            "DELETE FROM contacts WHERE id=?",
            (contact_id,)
        )

        conn.commit()

    conn.close()

    return redirect('/contacts')
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

   
