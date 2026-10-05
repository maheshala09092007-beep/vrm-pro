import mariadb
from database import get_connection



def add_vehicle():
    print("\n========== ADD VEHICLE ==========")

    registration_no = input("Registration Number: ").strip()
    brand = input("Brand: ").strip()
    model = input("Model: ").strip()
    vehicle_type = input("Vehicle Type: ").strip()

    try:
        price_per_day = float(input("Price Per Day: "))
    except ValueError:
        print("Invalid price.")
        return

    connection = get_connection()

    if not connection:
        return

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO vehicles
            (registration_no, brand, model, vehicle_type, price_per_day)
            VALUES (?, ?, ?, ?, ?)
        """, (
            registration_no,
            brand,
            model,
            vehicle_type,
            price_per_day
        ))

        connection.commit()

        print("\nVehicle added successfully!")

    except mariadb.Error as e:
        print(f"Error: {e}")

    finally:
        connection.close()


def view_vehicles():
    print("\n========== ALL VEHICLES ==========")

    connection = get_connection()

    if not connection:
        return

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT vehicle_id,
                   registration_no,
                   brand,
                   model,
                   vehicle_type,
                   price_per_day,
                   status
            FROM vehicles
            ORDER BY vehicle_id
        """)

        vehicles = cursor.fetchall()

        if not vehicles:
            print("No vehicles found.")
            return

        print("-" * 100)

        for v in vehicles:
            print(
                f"ID: {v[0]} | "
                f"{v[2]} {v[3]} | "
                f"Reg: {v[1]} | "
                f"Type: {v[4]} | "
                f"₹{v[5]}/day | "
                f"{v[6]}"
            )

        print("-" * 100)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        connection.close()


def search_vehicle():
    print("\n========== SEARCH VEHICLE ==========")

    keyword = input("Search by registration, brand or model: ").strip()

    connection = get_connection()

    if not connection:
        return

    try:
        cursor = connection.cursor()

        search = f"%{keyword}%"

        cursor.execute("""
            SELECT vehicle_id,
                   registration_no,
                   brand,
                   model,
                   vehicle_type,
                   price_per_day,
                   status
            FROM vehicles
            WHERE registration_no LIKE ?
               OR brand LIKE ?
               OR model LIKE ?
        """, (search, search, search))

        vehicles = cursor.fetchall()

        if not vehicles:
            print("No matching vehicles found.")
            return

        for v in vehicles:
            print(
                f"\nID: {v[0]}"
                f"\nRegistration: {v[1]}"
                f"\nVehicle: {v[2]} {v[3]}"
                f"\nType: {v[4]}"
                f"\nPrice: ₹{v[5]}/day"
                f"\nStatus: {v[6]}"
            )

    except Exception as e:
        print(f"Error: {e}")

    finally:
        connection.close()


def update_vehicle():
    print("\n========== UPDATE VEHICLE ==========")

    try:
        vehicle_id = int(input("Vehicle ID: "))
    except ValueError:
        print("Invalid ID.")
        return

    connection = get_connection()

    if not connection:
        return

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT brand, model, vehicle_type, price_per_day
            FROM vehicles
            WHERE vehicle_id = ?
        """, (vehicle_id,))

        vehicle = cursor.fetchone()

        if not vehicle:
            print("Vehicle not found.")
            return

        print("Press Enter to keep the existing value.")

        brand = input(f"Brand [{vehicle[0]}]: ").strip()
        model = input(f"Model [{vehicle[1]}]: ").strip()
        vehicle_type = input(f"Type [{vehicle[2]}]: ").strip()
        price = input(f"Price [{vehicle[3]}]: ").strip()

        brand = brand or vehicle[0]
        model = model or vehicle[1]
        vehicle_type = vehicle_type or vehicle[2]
        price = float(price) if price else vehicle[3]

        cursor.execute("""
            UPDATE vehicles
            SET brand = ?,
                model = ?,
                vehicle_type = ?,
                price_per_day = ?
            WHERE vehicle_id = ?
        """, (
            brand,
            model,
            vehicle_type,
            price,
            vehicle_id
        ))

        connection.commit()

        print("Vehicle updated successfully!")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        connection.close()


def delete_vehicle():
    print("\n========== DELETE VEHICLE ==========")

    try:
        vehicle_id = int(input("Vehicle ID: "))
    except ValueError:
        print("Invalid ID.")
        return

    connection = get_connection()

    if not connection:
        return

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT registration_no, brand, model
            FROM vehicles
            WHERE vehicle_id = ?
        """, (vehicle_id,))

        vehicle = cursor.fetchone()

        if not vehicle:
            print("Vehicle not found.")
            return

        cursor.execute("""
            SELECT COUNT(*)
            FROM bookings
            WHERE vehicle_id = ?
        """, (vehicle_id,))

        booking_count = cursor.fetchone()[0]

        if booking_count > 0:
            print(
                "Cannot delete this vehicle because "
                "booking records exist for it."
            )
            return

        confirm = input(
            f"Delete {vehicle[1]} {vehicle[2]} "
            f"({vehicle[0]})? (y/n): "
        )

        if confirm.lower() != "y":
            print("Deletion cancelled.")
            return

        cursor.execute("""
            DELETE FROM vehicles
            WHERE vehicle_id = ?
        """, (vehicle_id,))

        connection.commit()

        print("Vehicle deleted successfully!")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        connection.close()


def vehicle_menu():
    while True:
        print("\n===================================")
        print("        VEHICLE MANAGEMENT")
        print("===================================")
        print("1. Add Vehicle")
        print("2. View Vehicles")
        print("3. Search Vehicle")
        print("4. Update Vehicle")
        print("5. Delete Vehicle")
        print("6. Back")
        print("===================================")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_vehicle()
        elif choice == "2":
            view_vehicles()
        elif choice == "3":
            search_vehicle()
        elif choice == "4":
            update_vehicle()
        elif choice == "5":
            delete_vehicle()
        elif choice == "6":
            break
        else:
            print("Invalid choice.")
