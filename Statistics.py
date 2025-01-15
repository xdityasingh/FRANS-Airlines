import sqlite3
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Connect to the database
def connect_to_db():
    return sqlite3.connect("system_database.db")

# Fetch statistics
def fetch_statistics():
    conn = connect_to_db()
    cursor = conn.cursor()

    # Fetch seats data
    cursor.execute("SELECT COUNT(*) FROM seats WHERE status = 'available'")
    available_seats = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM seats WHERE status = 'reserved'")
    reserved_seats = cursor.fetchone()[0]

    total_seats = available_seats + reserved_seats
    available_percentage = (available_seats / total_seats) * 100 if total_seats > 0 else 0
    reserved_percentage = (reserved_seats / total_seats) * 100 if total_seats > 0 else 0

    # Fetch user data
    cursor.execute("SELECT id, name, email FROM users")
    users = cursor.fetchall()
    total_users = len(users)

    conn.close()
    return {
        "available_seats": available_seats,
        "reserved_seats": reserved_seats,
        "total_seats": total_seats,
        "available_percentage": available_percentage,
        "reserved_percentage": reserved_percentage,
        "users": users,
        "total_users": total_users,
    }

# Export statistics to a text file
def export_to_file(data):
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt", filetypes=[("Text files", "*.txt")], title="Save Statistics"
    )
    if not file_path:
        return

    with open(file_path, "w") as file:
        file.write(f"Available Seats: {data['available_seats']} ({data['available_percentage']:.2f}%)\n")
        file.write(f"Reserved Seats: {data['reserved_seats']} ({data['reserved_percentage']:.2f}%)\n")
        file.write(f"Total Seats: {data['total_seats']}\n\n")

        file.write("Users:\n")
        for user in data["users"]:
            file.write(f"ID: {user[0]}, Name: {user[1]}, Email: {user[2]}\n")
        file.write(f"\nTotal Users: {data['total_users']}\n")

    messagebox.showinfo("Export Successful", "Statistics exported successfully.")

# Display charts in GUI
def show_charts(data, root):
    # Create a new window for charts
    chart_window = tk.Toplevel(root)
    chart_window.title("Seat Statistics Visualization")

    fig, ax = plt.subplots(figsize=(5, 5))

    labels = ['Available Seats', 'Reserved Seats']
    sizes = [data['available_percentage'], data['reserved_percentage']]
    colors = ['green', 'red']
    explode = (0.1, 0)

    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
    ax.set_title("Seat Availability")

    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas.get_tk_widget().pack()
    canvas.draw()

# GUI Application
def admin_interface():
    root = tk.Tk()
    root.title("Admin Statistics Dashboard")
    root.geometry("600x400")
    root.resizable(False, False)

    data = fetch_statistics()

    # Header Label
    header = tk.Label(root, text="Admin Statistics Dashboard", font=("Helvetica", 16, "bold"))
    header.pack(pady=10)

    # Frame for buttons
    button_frame = tk.Frame(root)
    button_frame.pack(pady=20)

    # Display Area for Results
    results_frame = tk.Frame(root, borderwidth=2, relief="solid")
    results_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    results_text = tk.Text(results_frame, wrap=tk.WORD, height=10, font=("Courier", 10))
    results_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    # Functions for button actions
    def display_statistics():
        results_text.delete("1.0", tk.END)
        results_text.insert(tk.END, f"Available Seats: {data['available_seats']} ({data['available_percentage']:.2f}%)\n")
        results_text.insert(tk.END, f"Reserved Seats: {data['reserved_seats']} ({data['reserved_percentage']:.2f}%)\n")
        results_text.insert(tk.END, f"Total Seats: {data['total_seats']}\n")
        results_text.insert(tk.END, "\nUsers:\n")
        for user in data["users"]:
            results_text.insert(tk.END, f"ID: {user[0]}, Name: {user[1]}, Email: {user[2]}\n")
        results_text.insert(tk.END, f"\nTotal Users: {data['total_users']}")

    # Buttons
    btn_display_statistics = ttk.Button(button_frame, text="Display Statistics", command=display_statistics)
    btn_display_statistics.grid(row=0, column=0, padx=10)

    btn_export = ttk.Button(button_frame, text="Export Statistics", command=lambda: export_to_file(data))
    btn_export.grid(row=0, column=1, padx=10)

    btn_charts = ttk.Button(button_frame, text="Show Charts", command=lambda: show_charts(data, root))
    btn_charts.grid(row=0, column=2, padx=10)

    root.mainloop()

# Run the application
if __name__ == "__main__":
    admin_interface()
