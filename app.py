from flask import Flask, render_template, request, redirect
import sqlite3
import re

app = Flask(__name__)

ROOM_BEDS = {
    1: "2 Beds",
    2: "3 Beds",
    3: "2 Beds",
    4: "2 Beds",
    5: "1 Bed",
    6: "3 Beds"
}


@app.route("/")
def home():

    connection = sqlite3.connect("homestay.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM bookings")

    rows = cursor.fetchall()

    connection.close()

    booked_rooms = {}

    for row in rows:
        booked_rooms[int(row["room_number"])] = dict(row)

    total_rooms = 6
    booked_count = len(booked_rooms)
    available_count = total_rooms - booked_count

    return render_template(
        "index.html",
        room_beds=ROOM_BEDS,
        booked_rooms=booked_rooms,
        total_rooms=total_rooms,
        booked_count=booked_count,
        available_count=available_count
    )


@app.route("/book-room/<int:room_no>")
def book_room(room_no):

    connection = sqlite3.connect("homestay.db")
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM bookings
        WHERE room_number = ?
        """,
        (room_no,)
    )

    booking = cursor.fetchone()

    connection.close()

    if booking:
        return f"Room {room_no} is already booked."

    return render_template(
        "add_booking.html",
        room_no=room_no,
        bed_count=ROOM_BEDS[room_no]
    )


@app.route("/save-booking", methods=["POST"])
def save_booking():

    room_number = request.form["room_number"]
    guest_name = request.form["guest_name"]
    mobile = request.form["mobile"]
    address = request.form["address"]
    aadhaar = request.form["aadhaar"]
    vehicle_number = request.form["vehicle_number"]
    checkin_date = request.form["checkin_date"]
    checkout_date = request.form["checkout_date"]
    guest_count = request.form["guest_count"]

    if not re.fullmatch(r"\d{10}", mobile):
        return "Mobile number must contain exactly 10 digits."

    if aadhaar.strip() != "":
        if not re.fullmatch(r"\d{12}", aadhaar):
            return "Aadhaar number must contain exactly 12 digits."

    connection = sqlite3.connect("homestay.db")

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM bookings
        WHERE room_number = ?
        """,
        (room_number,)
    )

    existing_booking = cursor.fetchone()

    if existing_booking:
        connection.close()
        return "This room is already booked."

    cursor.execute(
        """
        INSERT INTO bookings
        (
            room_number,
            guest_name,
            mobile,
            address,
            aadhaar,
            vehicle_number,
            checkin_date,
            checkout_date,
            guest_count
        )
        VALUES
        (
            ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
        (
            room_number,
            guest_name,
            mobile,
            address,
            aadhaar,
            vehicle_number,
            checkin_date,
            checkout_date,
            guest_count
        )
    )

    connection.commit()
    connection.close()

    return redirect("/")


@app.route("/guest/<int:room_no>")
def guest_details(room_no):

    connection = sqlite3.connect("homestay.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM bookings
        WHERE room_number = ?
        """,
        (room_no,)
    )

    booking = cursor.fetchone()

    connection.close()

    if booking is None:
        return "Room not found."

    return render_template(
        "guest_details.html",
        booking=dict(booking)
    )


@app.route("/checkout/<int:booking_id>")
def checkout(booking_id):

    connection = sqlite3.connect("homestay.db")

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM bookings
        WHERE id = ?
        """,
        (booking_id,)
    )

    connection.commit()
    connection.close()

    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)