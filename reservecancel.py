import numpy as np
import pandas as pd

class SeatReservationSystem:
    def __init__(self, data_file):
        self.data_file = data_file
        self.seats = self.load_seats()

    def load_seats(self):
        try:
            return pd.read_csv(self.data_file)
        except FileNotFoundError:
            # Example DataFrame for testing
            data = {
                "Seat ID": ["1A", "1B", "2A", "2B"],
                "Status": ["available", "available", "occupied", "available"],
                "Category": ["business", "business", "economy", "economy"],
                "Price": [100, 100, 50, 50],
            }
            return pd.DataFrame(data)

    def save_seats(self):
        self.seats.to_csv(self.data_file, index=False)

    def reserve_seat(self, seat_id):
        if seat_id not in self.seats["Seat ID"].values:
            print("Error: Seat does not exist!")
            return

        seat_row = self.seats.loc[self.seats["Seat ID"] == seat_id]
        if seat_row.iloc[0]["Status"] == "occupied":
            print("Error: Seat is already reserved!")
        else:
            confirmation = input(f"Confirm reservation for seat {seat_id}? (yes/no): ").strip().lower()
            if confirmation == "yes":
                self.seats.loc[self.seats["Seat ID"] == seat_id, "Status"] = "occupied"
                self.save_seats()
                print(f"Seat {seat_id} reserved successfully!")

    def cancel_seat(self, seat_id):
        if seat_id not in self.seats["Seat ID"].values:
            print("Error: Seat does not exist!")
            return

        seat_row = self.seats.loc[self.seats["Seat ID"] == seat_id]
        if seat_row.iloc[0]["Status"] != "occupied":
            print("Error: Seat is not reserved!")
        else:
            confirmation = input(f"Confirm cancellation for seat {seat_id}? (yes/no): ").strip().lower()
            if confirmation == "yes":
                self.seats.loc[self.seats["Seat ID"] == seat_id, "Status"] = "available"
                self.save_seats()
                print(f"Reservation for seat {seat_id} canceled successfully!")

if __name__ == "__main__":
    system = SeatReservationSystem("seating_chart.csv")

    while True:
        print("\nSeat Reservation System")
        print("1. Reserve a Seat")
        print("2. Cancel a Reservation")
        print("3. View Seat Data")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            seat_id = input("Enter Seat ID to reserve: ")
            system.reserve_seat(seat_id)
        elif choice == "2":
            seat_id = input("Enter Seat ID to cancel: ")
            system.cancel_seat(seat_id)
        elif choice == "3":
            print("\nCurrent Seat Data:")
            print(system.seats)
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice! Please try again.")
