import pandas as pd
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Load data from CSV files or initialize if not available
def load_data():
    try:
        users = pd.read_csv('users.csv')
        seats = pd.read_csv('seats.csv')
    except FileNotFoundError:
        # Initialize with sample data if files don't exist
        users = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Admin User", "User One", "User Two"],
                "email": ["admin@example.com", "user1@example.com", "user2@example.com"],
            }
        )
        seats = pd.DataFrame(
            {
                "seat_id": [1, 2, 3, 4, 5],
                "status": ["available", "reserved", "available", "reserved", "available"],
                "category": ["economy", "business", "first", "economy", "business"],
                "price": [100.0, 300.0, 500.0, 120.0, 400.0],
            }
        )
    return users, seats

# Save data to CSV files
def save_data(users, seats):
    users.to_csv('users.csv', index=False)
    seats.to_csv('seats.csv', index=False)

# Fetch statistics
def fetch_statistics(users, seats):
    available_seats = seats[seats["status"] == "available"].shape[0]
    reserved_seats = seats[seats["status"] == "reserved"].shape[0]
    total_seats = len(seats)

    available_percentage = (available_seats / total_seats) * 100 if total_seats > 0 else 0
    reserved_percentage = (reserved_seats / total_seats) * 100 if total_seats > 0 else 0

    return {
        "available_seats": available_seats,
        "reserved_seats": reserved_seats,
        "total_seats": total_seats,
        "available_percentage": available_percentage,
        "reserved_percentage": reserved_percentage,
        "users": users,
        "total_users": len(users),
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
        for _, user in data["users"].iterrows():
            file.write(f"ID: {user['id']}, Name: {user['name']}, Email: {user['email']}\n")
        file.write(f"\nTotal Users: {data['total_users']}\n")

    messagebox.showinfo("Export Successful", "Statistics exported successfully.")

# Display charts in GUI
def show_charts(data, root):
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

    users, seats = load_data()
    data = fetch_statistics(users, seats)

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

    def display_statistics():
        results_text.delete("1.0", tk.END)
        results_text.insert(tk.END, f"Available Seats: {data['available_seats']} ({data['available_percentage']:.2f}%)\n")
        results_text.insert(tk.END, f"Reserved Seats: {data['reserved_seats']} ({data['reserved_percentage']:.2f}%)\n")
        results_text.insert(tk.END, f"Total Seats: {data['total_seats']}\n")
        results_text.insert(tk.END, "\nUsers:\n")
        for _, user in users.iterrows():
            results_text.insert(tk.END, f"ID: {user['id']}, Name: {user['name']}, Email: {user['email']}\n")
        results_text.insert(tk.END, f"\nTotal Users: {data['total_users']}")

    btn_display_statistics = ttk.Button(button_frame, text="Display Statistics", command=display_statistics)
    btn_display_statistics.grid(row=0, column=0, padx=10)

    btn_export = ttk.Button(button_frame, text="Export Statistics", command=lambda: export_to_file(data))
    btn_export.grid(row=0, column=1, padx=10)

    btn_charts = ttk.Button(button_frame, text="Show Charts", command=lambda: show_charts(data, root))
    btn_charts.grid(row=0, column=2, padx=10)

    root.mainloop()

if __name__ == "__main__":
    admin_interface()
