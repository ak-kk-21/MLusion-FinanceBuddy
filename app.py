from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import re
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

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

def categorize_transaction(vendor, amount, text):
    """Stub: Replace this with actual ML or rule-based logic"""
    if "zomato" in vendor.lower():
        return "Food"
    elif "amazon" in vendor.lower():
        return "Shopping"
    elif "petrol" in text.lower() or "fuel" in text.lower():
        return "Transport"
    else:
        return "Uncategorized"

def parse_sms(sms_text):
    """Extracts amount, timestamp, vendor, account (if available)"""
    amount_match = re.search(r'₹?\s?(\d+(?:\.\d{1,2})?)', sms_text)
    timestamp_match = re.search(r'on\s+(\d{4}-\d{2}-\d{2}[\sT]?\d{2}:\d{2})', sms_text)
    vendor_match = re.search(r'to\s+([\w\s&.-]+)', sms_text, re.IGNORECASE)
    account_match = re.search(r'from\s+(\w+)', sms_text, re.IGNORECASE)

    amount = float(amount_match.group(1)) if amount_match else 0.0
    timestamp = timestamp_match.group(1) if timestamp_match else datetime.now().strftime("%Y-%m-%d %H:%M")
    vendor = vendor_match.group(1).strip() if vendor_match else "Unknown"
    account_name = account_match.group(1).strip() if account_match else "Unknown"

    return amount, timestamp, vendor, account_name

@app.route('/sms_category', methods=['GET', 'POST'])
def sms_category():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to use this feature.", "warning")
        return redirect('/login')

    if request.method == 'POST':
        sms_input = request.form['sms_input']
        amount, timestamp, vendor, account_name = parse_sms(sms_input)
        category = categorize_transaction(vendor, amount, sms_input)

        # Find account_id from account_name if exists
        conn = sqlite3.connect('financebuddy.db')
        c = conn.cursor()

        c.execute("SELECT account_id FROM Accounts WHERE user_id = ? AND bank_name = ?", (user_id, account_name))
        acc = c.fetchone()
        if acc:
            account_id = acc[0]
        else:
            # Create new account entry
            c.execute("INSERT INTO Accounts (user_id, bank_name) VALUES (?, ?)", (user_id, account_name))
            account_id = c.lastrowid

        # Insert transaction
        c.execute('''INSERT INTO Expenses 
                     (user_id, account_id, timestamp, amount, vendor, category, raw_text) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (user_id, account_id, timestamp, amount, vendor, category, sms_input))
        conn.commit()
        conn.close()

        # Pass categorized data to the output page via session
        session['categorized_sms'] = {
            'timestamp': timestamp,
            'vendor': vendor,
            'amount': amount,
            'category': category
        }

        return redirect('/categorized_output')

    return render_template('sms_category.html')


@app.route('/categorized_output')
def categorized_output():
    categorized_sms = session.get('categorized_sms')
    if not categorized_sms:
        flash("No transaction categorized yet.", "warning")
        return redirect('/sms_category')

    return render_template('categorized_output.html', categorized_sms=categorized_sms)

if __name__ == '__main__':
    app.run(debug=True)
