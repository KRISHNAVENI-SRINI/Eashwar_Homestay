import sqlite3

connection = sqlite3.connect("homestay.db")

cursor = connection.cursor()

cursor.execute("DROP TABLE IF EXISTS bookings")

cursor.execute("""
CREATE TABLE bookings (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    room_number INTEGER,

    guest_name TEXT,

    mobile TEXT,

    address TEXT,

    aadhaar TEXT,

    vehicle_number TEXT,

    checkin_date TEXT,

    checkout_date TEXT,

    guest_count INTEGER
)
""")

connection.commit()
connection.close()

print("Database recreated successfully!")