from flask import Flask, jsonify, request, render_template
import mysql.connector
import re
import bcrypt

app = Flask(__name__)

def hash_password(password):
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password

def check_password(plain_password, hashed_password):
    plain_password_bytes = plain_password.encode('utf-8')
    return bcrypt.checkpw(plain_password_bytes, hashed_password)

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def is_valid_password(password):
    password_regex = r'^[A-Za-z0-9]{8,}$'
    return re.match(password_regex, password) is not None

def get_db_connection():
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password="sobirov0909",
        database="loyiha"
    )

    if con.is_connected():
        print("Ulandi...")
    else:
        print("Ulanmadi")
    return con


@app.route("/", methods=['GET'])
def home():
    return render_template("main.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        name = data['name'].strip()
        surname = data['surname'].strip()
        age = data['age']
        gender = data['gender']
        email = data['email'].strip()
        password = data['password'].strip()
        repassword = data['repassword'].strip()
        if len(name) < 2:
            return jsonify({"message": "Name is not full"})
        if len(surname) < 2:
            return jsonify({"message": "surname is not full"})
        if int(age) < 15 or int(age) > 200:
            return jsonify({"message": "Age incorrect"})
        if gender.lower() != "erkak" and gender.lower() != "ayol":
            return jsonify({"message": "Gender incorrect"})
        if not is_valid_email(email):
            return jsonify({"massage": "Email incorrect"})
        if password != repassword:
            return jsonify({"massage": "password and repassword not equal"})
        if not is_valid_password(password):
            return jsonify({"massage": "password incorrect"})
        
        
        con = get_db_connection()
        cur = con.cursor(dictionary=True)
        sql = "create table if not exists users (id int auto_increment primary key, name varchar(50), surname varchar(50), age int, gender varchar(10), email varchar(255), password varchar(255))"
        cur.execute(sql)
        sql = "insert into users(name, surname, age, gender, email, password) values (%s, %s, %s, %s, %s, %s)"
        val = (name, surname, age, gender, email, hash_password(password))
        cur.execute(sql, val)
        print("register")
        con.commit()
        con.close()
        return render_template("main.html")
    
        
    return render_template("register.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        login_email = data['login_email'].strip()
        login_password = data['login_password'].strip()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            cursor.execute("SELECT * FROM users WHERE email = %s", (login_email,))
            
            user = cursor.fetchone()

            cursor.fetchall() 

            if user and bcrypt.checkpw(login_password.encode('utf-8'), user['password'].encode('utf-8')):
                return render_template("added.html")
            else:
                return jsonify({"message": "Email yoki parol noto'g'ri"}), 401

        finally:
            cursor.close()
            conn.close()

    return render_template("login.html")





















if __name__ == "__main__":
    app.run(debug=True, port=8080)
