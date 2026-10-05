from database import get_connection
from datetime import datetime


def generate_bill():
    print("\n========== GENERATE BILL ==========")

    try:
        booking_id = int(input("Booking ID: "))
    except ValueError:
        print("Invalid booking ID.")
        return

    connection = get_connection()

    if not connection:
        return

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                b.booking_id,
                c.name,
                v.brand,
                v.model,
                v.price_per_day,
                b.start_date,
                b.end_date,
                b.status
            FROM bookings b
            JOIN customers c
                ON b.customer_id = c.customer_id
            JOIN vehicles v
                ON b.vehicle_id = v.vehicle_id
            WHERE b.booking_id = ?
        """, (booking_id,))

        booking = cursor.fetchone()

        if not booking:
            print("Booking not found.")
            return

        # Check whether bill already exists
        cursor.execute("""
            SELECT bill_id
            FROM bills
            WHERE booking_id = ?
        """, (booking_id,))

        existing_bill = cursor.fetchone()

        if existing_bill:
            print(
                f"Bill already exists. "
                f"Bill ID: {existing_bill[0]}"
            )
            return

        start_date = booking[5]
        end_date = booking[6]

        days = (end_date - start_date).days

        if days <= 0:
            print("Invalid booking duration.")
            return

        rental_amount = days * float(booking[4])

        print("\n========== BILL ==========")
        print(f"Booking ID: {booking[0]}")
        print(f"Customer: {booking[1]}")
        print(f"Vehicle: {booking[2]} {booking[3]}")
        print(f"From: {start_date}")
        print(f"To: {end_date}")
        print(f"Rental Days: {days}")
        print(f"Price/Day: ₹{booking[4]}")
        print(f"Rental Amount: ₹{rental_amount:.2f}")

        try:
            extra_charges = float(
                input("Extra Charges: ")
            )
        except ValueError:
            extra_charges = 0

        total_amount = rental_amount + extra_charges

        print(f"Total Amount: ₹{total_amount:.2f}")

        confirm = input("Generate bill? (y/n): ")

        if confirm.lower() != "y":
            print("Bill generation cancelled.")
            return

        payment_method = input(
            "Payment Method (Cash/UPI/Card): "
        ).strip()

        if payment_method not in ["Cash", "UPI", "Card"]:
            print("Invalid payment method.")
            return

        cursor.execute("""
            INSERT INTO bills
            (
                booking_id,
                rental_amount,
                extra_charges,
                total_amount,
                payment_status,
                payment_method,
                bill_date
            )
            VALUES (?, ?, ?, ?, 'Pending', ?, CURDATE())
        """, (
            booking_id,
            rental_amount,
            extra_charges,
            total_amount,
            payment_method
        ))

        connection.commit()

        print("\nBill generated successfully!")
        print(f"Total: ₹{total_amount:.2f}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        connection.close()


def view_bills():
    print("\n========== ALL BILLS ==========")

    connection = get_connection()

    if not connection:
        return

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                bl.bill_id,
                bl.booking_id,
                c.name,
                CONCAT(v.brand, ' ', v.model),
                bl.rental_amount,
                bl.extra_charges,
                bl.total_amount,
                bl.payment_status,
                bl.payment_method,
                bl.bill_date
            FROM bills bl
            JOIN bookings b
                ON bl.booking_id = b.booking_id
            JOIN customers c
                ON b.customer_id = c.customer_id
            JOIN vehicles v
                ON b.vehicle_id = v.vehicle_id
            ORDER BY bl.bill_id DESC
        """)

        bills = cursor.fetchall()

        if not bills:
            print("No bills found.")
            return

        for bill in bills:
            print(
                f"\nBill ID: {bill[0]}"
                f"\nBooking ID: {bill[1]}"
                f"\nCustomer: {bill[2]}"
                f"\nVehicle: {bill[3]}"
                f"\nRental: ₹{bill[4]}"
                f"\nExtra Charges: ₹{bill[5]}"
                f"\nTotal: ₹{bill[6]}"
                f"\nPayment: {bill[7]}"
                f"\nMethod: {bill[8]}"
                f"\nDate: {bill[9]}"
            )
            print("-" * 40)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        connection.close()


def mark_payment():
    print("\n========== MARK PAYMENT ==========")

    try:
        bill_id = int(input("Bill ID: "))
    except ValueError:
        print("Invalid bill ID.")
        return

    connection = get_connection()

    if not connection:
        return

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE bills
            SET payment_status = 'Paid'
            WHERE bill_id = ?
        """, (bill_id,))

        connection.commit()

        if cursor.rowcount == 0:
            print("Bill not found.")
        else:
            print("Payment marked as PAID.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        connection.close()


def billing_menu():
    while True:
        print("\n===================================")
        print("             BILLING")
        print("===================================")
        print("1. Generate Bill")
        print("2. View Bills")
        print("3. Mark Payment")
        print("4. Back")
        print("===================================")

        choice = input("Enter your choice: ")

        if choice == "1":
            generate_bill()
        elif choice == "2":
            view_bills()
        elif choice == "3":
            mark_payment()
        elif choice == "4":
            break
        else:
            print("Invalid choice.")
