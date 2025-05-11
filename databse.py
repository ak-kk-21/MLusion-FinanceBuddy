# database.py
import sqlite3

def init_db():
    conn = sqlite3.connect('financebuddy.db')
    c = conn.cursor()

    # Create Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')


    # Create Accounts table
    c.execute('''
        CREATE TABLE IF NOT EXISTS Accounts (
            account_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            bank_name TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
    ''')

    # Create Expenses table
    c.execute('''
        CREATE TABLE IF NOT EXISTS Expenses (
            expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            account_id INTEGER,
            timestamp TEXT,
            amount REAL,
            vendor TEXT,
            category TEXT,
            is_anomalous INTEGER DEFAULT 0,
            raw_text TEXT,
            FOREIGN KEY (user_id) REFERENCES Users(user_id),
            FOREIGN KEY (account_id) REFERENCES Accounts(account_id)
        )
    ''')

    conn.commit()
    conn.close()
def main():
    init_db()
    print("Database created successfully!")  
if __name__ == "__main__":

    main()
