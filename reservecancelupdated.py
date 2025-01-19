# THIS IS AN UPDATED VERSION AND PROBABLY A MORE REFINED DRAFT

import csv

def reserve_seat(seat_id):
    updated = False
    rows = []
    with open("seating_chart.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Seat ID"] == seat_id:
                if row["Status"] == "available":
                    row["Status"] = "occupied"
                    updated = True
                else:
                    return False, "Seat already reserved."
            rows.append(row)
    if updated:
        with open("seating_chart.csv", "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        return True, "Seat reserved successfully."
    return False, "Seat not found."

def cancel_reservation(seat_id):
    updated = False
    rows = []
    with open("seating_chart.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Seat ID"] == seat_id:
                if row["Status"] == "occupied":
                    row["Status"] = "available"
                    updated = True
                else:
                    return False, "Seat is not reserved."
            rows.append(row)
    if updated:
        with open("seating_chart.csv", "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        return True, "Reservation canceled successfully."
    return False, "Seat not found."