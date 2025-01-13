import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import time

# Database setup functions (same as your original code)
def initialize_database():
    conn = sqlite3.connect('seats.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS seats (seat_id INTEGER PRIMARY KEY, status INTEGER, user_name TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS seat_count (id INTEGER PRIMARY KEY, remaining_seats INTEGER)''')
    
    for i in range(1, 26):  # 25 seats
        c.execute('INSERT OR IGNORE INTO seats (seat_id, status, user_name) VALUES (?, ?, ?)', (i, 0, None))
    
    c.execute('INSERT OR IGNORE INTO seat_count (id, remaining_seats) VALUES (1, 25)')
    
    conn.commit()
    conn.close()

def fetch_seat_status():
    conn = sqlite3.connect('seats.db')
    c = conn.cursor()
    c.execute('SELECT * FROM seats')
    seats = c.fetchall()
    conn.close()
    return seats

def update_seat_status_in_db(seat_id, status):
    conn = sqlite3.connect('seats.db')
    c = conn.cursor()
    c.execute('UPDATE seats SET status = ? WHERE seat_id = ?', (status, seat_id))
    conn.commit()
    conn.close()

def store_user_name_in_db(seat_id, user_name):
    conn = sqlite3.connect('seats.db')
    c = conn.cursor()
    c.execute('UPDATE seats SET user_name = ? WHERE seat_id = ?', (user_name, seat_id))
    conn.commit()
    conn.close()

def fetch_remaining_seats():
    conn = sqlite3.connect('seats.db')
    c = conn.cursor()
    c.execute('SELECT remaining_seats FROM seat_count WHERE id = 1')
    remaining_seats = c.fetchone()[0]
    conn.close()
    return remaining_seats

def update_remaining_seats_in_db(remaining_seats):
    conn = sqlite3.connect('seats.db')
    c = conn.cursor()
    c.execute('UPDATE seat_count SET remaining_seats = ? WHERE id = 1', (remaining_seats,))
    conn.commit()
    conn.close()

class MovieTicketBookingSystem:
    def __init__(self, total_seats):
        self.total_seats = total_seats
        initialize_database()

    def book_seat(self, user_name, seat_number, update_seat_label, update_seat_color):
        seat_id = seat_number + 1
        if fetch_seat_status()[seat_number][1] == 0:
            update_seat_status_in_db(seat_id, 1)
            store_user_name_in_db(seat_id, user_name)
            remaining_seats = fetch_remaining_seats() - 1
            update_remaining_seats_in_db(remaining_seats)
            update_seat_label(f"Seats remaining: {remaining_seats}")
            update_seat_color(seat_number, "red")
            messagebox.showinfo("Booking Successful", f"{user_name} successfully booked seat {seat_number + 1}")
        else:
            messagebox.showwarning("Booking Failed", f"Seat {seat_number + 1} is already booked.")

    def reset_all_seats(self, update_seat_label, update_seat_color):
        for seat_number in range(self.total_seats):
            update_seat_status_in_db(seat_number + 1, 0)
            store_user_name_in_db(seat_number + 1, None)
            update_seat_color(seat_number, "lightgreen")
        update_remaining_seats_in_db(self.total_seats)
        update_seat_label(f"Seats remaining: {self.total_seats}")
        messagebox.showinfo("Reset Successful", "Admin has reset the seats. All seats are now available.")

def open_user_booking_window(user_name, booking_system, update_seat_label, update_seat_color):
    def select_seat(seat_number):
        if fetch_seat_status()[seat_number][1] == 0:
            booking_system.book_seat(user_name, seat_number, update_seat_label, update_seat_color)
        else:
            messagebox.showwarning("Seat Already Booked", f"Seat {seat_number + 1} is already booked.")

    window = tk.Tk()
    window.title(f"{user_name} Booking")
    window.geometry("600x450")

    tk.Label(window, text=f"Welcome, {user_name}", font=("Helvetica", 14)).grid(row=0, column=0, pady=10)

    seat_buttons = []
    num_rows = 5
    num_cols = 5
    seat_counter = 0

    for row in range(num_rows):
        for col in range(num_cols):
            seat_button = tk.Button(window, text=f"Seat {seat_counter + 1}", width=12, height=2,
                                    command=lambda seat=seat_counter: select_seat(seat))
            seat_button.grid(row=row + 1, column=col, padx=5, pady=5)
            seat_buttons.append(seat_button)
            seat_counter += 1

    def update_seat_label(text):
        seat_label.config(text=text)

    def update_seat_color(seat_number, color):
        seat_buttons[seat_number].config(bg=color)

    seat_label = tk.Label(window, text=f"Seats remaining: {booking_system.total_seats}", font=("Helvetica", 14))
    seat_label.grid(row=num_rows + 1, column=0, columnspan=num_cols, pady=10)

    def update_seat_status():
        seats = fetch_seat_status()
        remaining_seats = fetch_remaining_seats()
        update_seat_label(f"Seats remaining: {remaining_seats}")
        for i in range(booking_system.total_seats):
            color = "red" if seats[i][1] == 1 else "lightgreen"
            update_seat_color(i, color)
        window.after(1000, update_seat_status)  # Call this function again after 1 second

    update_seat_status()
    window.mainloop()

def open_admin_dashboard(booking_system):
    def reset_seats():
        booking_system.reset_all_seats(update_seat_label, update_seat_color)

    window = tk.Tk()
    window.title("Admin Dashboard")
    window.geometry("810x500")

    tk.Label(window, text="Admin Dashboard", font=("Helvetica", 16)).grid(row=0, column=0, pady=10)

    seat_label = tk.Label(window, text=f"Seats remaining: {booking_system.total_seats}", font=("Helvetica", 14))
    seat_label.grid(row=1, column=0, pady=10)

    tk.Button(window, text="Reset All Seats", command=reset_seats).grid(row=2, column=0, pady=10)

    seat_buttons = []
    num_rows = 5
    num_cols = 5
    seat_counter = 0

    for row in range(num_rows):
        for col in range(num_cols):
            seat_button = tk.Button(window, text=f"Seat {seat_counter + 1}", width=20, height=3)
            seat_button.grid(row=row + 3, column=col, padx=5, pady=5)
            seat_buttons.append(seat_button)
            seat_counter += 1

    def update_seat_label(text):
        seat_label.config(text=text)

    def update_seat_color(seat_number, color):
        seat_buttons[seat_number].config(bg=color)

    def update_seat_status():
        seats = fetch_seat_status()
        remaining_seats = fetch_remaining_seats()
        update_seat_label(f"Seats remaining: {remaining_seats}")
        for i in range(booking_system.total_seats):
            color = "red" if seats[i][1] == 1 else "lightgreen"
            seat_buttons[i].config(text=f"Seat {i + 1}\nBooked by: {seats[i][2] if seats[i][2] else 'Available'}")
            update_seat_color(i, color)
        window.after(1000, update_seat_status)  # Call this function again after 1 second

    update_seat_status()
    window.mainloop()

def ask_user_count_and_names():
    user_count = simpledialog.askinteger("Number of Users", "Enter the number of users:", minvalue=1, maxvalue=5)
    if user_count is None or user_count < 1:
        messagebox.showerror("Error", "Invalid number of users.")
        return

    user_names = []
    for i in range(user_count):
        name = simpledialog.askstring(f"User {i + 1}", f"Enter name for User {i + 1}:")
        if name:
            user_names.append(name)
        else:
            messagebox.showerror("Error", "All user names are required.")
            return None
    
    return user_names

if __name__ == "__main__":
    user_names = ask_user_count_and_names()
    
    if user_names:
        booking_system = MovieTicketBookingSystem(total_seats=25)

        # Open user booking windows sequentially
        for user_name in user_names:
            open_user_booking_window(user_name, booking_system, open_admin_dashboard, open_admin_dashboard)

        # Open the admin dashboard
        open_admin_dashboard(booking_system)

