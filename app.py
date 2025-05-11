from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)

        conn = sqlite3.connect('financebuddy.db')
        c = conn.cursor()
        c.execute("INSERT INTO Users (name, password) VALUES (?, ?)", (name, hashed_pw))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        conn = sqlite3.connect('financebuddy.db')
        c = conn.cursor()
        c.execute("SELECT user_id, password FROM Users WHERE name = ?", (name,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            flash('Login successful!', 'success')
            return redirect('/')
        else:
            flash('Invalid username or password', 'danger')
            return redirect('/login')

    return render_template('login.html')

# @app.route('/sms_category', methods=['GET', 'POST'])
# def sms_category():
#     user_id = session.get('user_id')
#     if not user_id:
#         flash("Please log in to view your SMS categories.", "warning")
#         return redirect('/login')

#     if request.method == 'POST':
#         sms_input = request.form['sms_input']
#         # You’ll need to implement: parse_sms_and_insert_to_db(sms_input, user_id)
#         # Then update category field using your ML model

#     categories = get_category_data_for_user(user_id)
#     return render_template('sms_category.html', categories=dict(categories))


# def get_category_data_for_user(user_id):
#     # Fetch category-wise data from the database for the user
#     conn = sqlite3.connect('financebuddy.db')
#     c = conn.cursor()
#     c.execute('''
#         SELECT category, SUM(amount) 
#         FROM Expenses 
#         WHERE user_id = ? 
#         GROUP BY category
#     ''', (user_id,))
#     data = c.fetchall()
#     conn.close()
    
#     # Return data in a dict format
#     return {category: amount for category, amount in data}

if __name__ == '__main__':
    app.run(debug=True)

