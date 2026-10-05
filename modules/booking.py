from database import get_connection


def show_available_vehicles():
    print("\n========== AVAILABLE VEHICLES ==========")

    start_date = input("Start Date (YYYY-MM-DD): ").strip()
    end_date = input("End Date (YYYY-MM-DD): ").strip()

    connection = get_connection()

    if not connection:
        return

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                v.vehicle_id,
                v.registration_no,
                v.brand,
                v.model,
                v.vehicle_type,
                v.price_per_day
            FROM vehicles v
            WHERE v.status != 'Maintenance'
            AND NOT EXISTS (
                SELECT 1
                FROM bookings b
                WHERE b.vehicle_id = v.vehicle_id
                AND b.status = 'Confirmed'
                AND b.start_date < ?
                AND b.end_date > ?
            )
        """, (end_date, start_date))

        vehicles = cursor.fetchall()

        if not vehicles:
            print("No vehicles available for these dates.")
            return

        for v in vehicles:
            print(
                f"\nID: {v[0]}"
                f"\nRegistration: {v[1]}"
                f"\nVehicle: {v[2]} {v[3]}"
                f"\nType: {v[4]}"
                f"\nPrice: ₹{v[5]}/day"
            )

    except Exception as e:
        print(f"Error: {e}")

    finally:
        connection.close()


def create_booking():
    print("\n========== CREATE BOOKING ==========")

    try:
        customer_id = int(input("Customer ID: "))
        vehicle_id = int(input("Vehicle ID: "))
    except ValueError:
        print("Invalid ID.")
        return

    start_date = input("Start Date (YYYY-MM-DD): ").strip()
    end_date = input("End Date (YYYY-MM-DD): ").strip()

    connection = get_connection()

    if not connection:
        return

    try:
        cursor = connection.cursor()

        # Check customer
        cursor.execute("""
            SELECT name
            FROM customers
            WHERE customer_id = ?
        """, (customer_id,))

        customer = cursor.fetchone()

        if not customer:
            print("Customer not found.")
            return

        # Check vehicle
        cursor.execute("""
            SELECT brand, model, price_per_day, status
            FROM vehicles
            WHERE vehicle_id = ?
        """, (vehicle_id,))

        vehicle = cursor.fetchone()

        if not vehicle:
            print("Vehicle not found.")
            return

        if vehicle[3] == "Maintenance":
            print("Vehicle is under maintenance.")
            return

        # Check overlapping booking
        cursor.execute("""
            SELECT COUNT(*)
            FROM bookings
            WHERE vehicle_id = ?
            AND status = 'Confirmed'
            AND start_date < ?
            AND end_date > ?
        """, (
            vehicle_id,
            end_date,
            start_date
        ))

        overlap = cursor.fetchone()[0]

        if overlap > 0:
            print(
                "\nVehicle is already booked "
                "for the selected dates."
            )
            return

        # Validate dates
        from datetime import datetime

        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        if end <= start:
            print("End date must be after start date.")
            return

        days = (end - start).days

        estimated_amount = days * float(vehicle[2])

        print("\n========== BOOKING SUMMARY ==========")
        print(f"Customer: {customer[0]}")
        print(f"Vehicle: {vehicle[0]} {vehicle[1]}")
        print(f"Days: {days}")
        print(f"Estimated Amount: ₹{estimated_amount:.2f}")

        confirm = input("\nConfirm booking? (y/n): ")

        if confirm.lower() != "y":
            print("Booking cancelled.")
            return

        cursor.execute("""
            INSERT INTO bookings
            (customer_id, vehicle_id, start_date, end_date, status)
            VALUES (?, ?, ?, ?, 'Confirmed')
        """, (
            customer_id,
            vehicle_id,
            start_date,
            end_date
        ))

        connection.commit()

        booking_id = cursor.lastrowid

        print("\nBooking created successfully!")
        print(f"Booking ID: {booking_id}")

    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        connection.close()


def view_bookings():
    print("\n========== ALL BOOKINGS ==========")

    connection = get_connection()

    if not connection:
        return

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                b.booking_id,
                c.name,
                CONCAT(v.brand, ' ', v.model),
                v.registration_no,
                b.start_date,
                b.end_date,
                b.status
            FROM bookings b
            JOIN customers c
                ON b.customer_id = c.customer_id
            JOIN vehicles v
                ON b.vehicle_id = v.vehicle_id
            ORDER BY b.booking_id DESC
        """)

        bookings = cursor.fetchall()

        if not bookings:
            print("No bookings found.")
            return

        for b in bookings:
            print(
                f"\nBooking ID: {b[0]}"
                f"\nCustomer: {b[1]}"
                f"\nVehicle: {b[2]}"
                f"\nRegistration: {b[3]}"
                f"\nFrom: {b[4]}"
                f"\nTo: {b[5]}"
                f"\nStatus: {b[6]}"
            )
            print("-" * 40)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        connection.close()


def cancel_booking():
    print("\n========== CANCEL BOOKING ==========")

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
            SELECT status
            FROM bookings
            WHERE booking_id = ?
        """, (booking_id,))

        booking = cursor.fetchone()

        if not booking:
            print("Booking not found.")
            return

        if booking[0] != "Confirmed":
            print("Only confirmed bookings can be cancelled.")
            return

        cursor.execute("""
            UPDATE bookings
            SET status = 'Cancelled'
            WHERE booking_id = ?
        """, (booking_id,))

        connection.commit()

        print("Booking cancelled successfully.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        connection.close()


def complete_booking():
    print("\n========== COMPLETE BOOKING ==========")

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
            UPDATE bookings
            SET status = 'Completed'
            WHERE booking_id = ?
            AND status = 'Confirmed'
        """, (booking_id,))

        connection.commit()

        if cursor.rowcount == 0:
            print("Booking not found or already completed.")
        else:
            print("Booking marked as completed.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        connection.close()


def booking_menu():
    while True:
        print("\n===================================")
        print("           BOOKING")
        print("===================================")
        print("1. Check Vehicle Availability")
        print("2. Create Booking")
        print("3. View Bookings")
        print("4. Cancel Booking")
        print("5. Complete Booking")
        print("6. Back")
        print("===================================")

        choice = input("Enter your choice: ")

        if choice == "1":
            show_available_vehicles()
        elif choice == "2":
            create_booking()
        elif choice == "3":
            view_bookings()
        elif choice == "4":
            cancel_booking()
        elif choice == "5":
            complete_booking()
        elif choice == "6":
            break
        else:
            print("Invalid choice.")
