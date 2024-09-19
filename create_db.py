import sqlite3


def create_vacation_db():
    conn = sqlite3.connect('vacations.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS vacations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_name TEXT NOT NULL,
                    cover_name TEXT NOT NULL,
                    vacation_date TEXT NOT NULL,
                    author TEXT NOT NULL
                 )''')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_vacation_db()
