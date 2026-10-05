from database import get_connection


def add_customer():
    print("\n========== ADD CUSTOMER ==========")

    name = input("Name: ").strip()
    phone = input("Phone: ").strip()
    email = input("Email: ").strip()
    license_number = input("License Number: ").strip()
    address = input("Address: ").strip()

    connection = get_connection()

    if not connection:
        return

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO customers
            (name, phone, email, license_number, address)
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            phone,
            email,
            license_number,
            address
        ))

        connection.commit()

        print("\nCustomer added successfully!")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        connection.close()


def view_customers():
    print("\n========== ALL CUSTOMERS ==========")

    connection = get_connection()

    if not connection:
        return

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT customer_id,
                   name,
                   phone,
                   email,
                   license_number,
                   address
            FROM customers
            ORDER BY customer_id
        """)

        customers = cursor.fetchall()

        if not customers:
            print("No customers found.")
            return

        for c in customers:
            print(
                f"\nID: {c[0]}"
                f"\nName: {c[1]}"
                f"\nPhone: {c[2]}"
                f"\nEmail: {c[3]}"
                f"\nLicense: {c[4]}"
                f"\nAddress: {c[5]}"
            )
            print("-" * 40)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        connection.close()


def search_customer():
    print("\n========== SEARCH CUSTOMER ==========")

    keyword = input("Enter name, phone or license number: ").strip()

    connection = get_connection()

    if not connection:
        return

    try:
        cursor = connection.cursor()

        search = f"%{keyword}%"

        cursor.execute("""
            SELECT customer_id,
                   name,
                   phone,
                   email,
                   license_number
            FROM customers
            WHERE name LIKE ?
               OR phone LIKE ?
               OR license_number LIKE ?
        """, (search, search, search))

        customers = cursor.fetchall()

        if not customers:
            print("No customers found.")
            return

        for c in customers:
            print(
                f"\nID: {c[0]}"
                f"\nName: {c[1]}"
                f"\nPhone: {c[2]}"
                f"\nEmail: {c[3]}"
                f"\nLicense: {c[4]}"
            )

    except Exception as e:
        print(f"Error: {e}")

    finally:
        connection.close()


def update_customer():
    print("\n========== UPDATE CUSTOMER ==========")

    try:
        customer_id = int(input("Customer ID: "))
    except ValueError:
        print("Invalid ID.")
        return

    connection = get_connection()

    if not connection:
        return

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT name, phone, email, license_number, address
            FROM customers
            WHERE customer_id = ?
        """, (customer_id,))

        customer = cursor.fetchone()

        if not customer:
            print("Customer not found.")
            return

        print("Press Enter to keep the existing value.")

        name = input(f"Name [{customer[0]}]: ").strip()
        phone = input(f"Phone [{customer[1]}]: ").strip()
        email = input(f"Email [{customer[2]}]: ").strip()
        address = input(f"Address [{customer[4]}]: ").strip()

        name = name or customer[0]
        phone = phone or customer[1]
        email = email or customer[2]
        address = address or customer[4]

        cursor.execute("""
            UPDATE customers
            SET name = ?,
                phone = ?,
                email = ?,
                address = ?
            WHERE customer_id = ?
        """, (
            name,
            phone,
            email,
            address,
            customer_id
        ))

        connection.commit()

        print("Customer updated successfully!")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        connection.close()


def delete_customer():
    print("\n========== DELETE CUSTOMER ==========")

    try:
        customer_id = int(input("Customer ID: "))
    except ValueError:
        print("Invalid ID.")
        return

    connection = get_connection()

    if not connection:
        return

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT name
            FROM customers
            WHERE customer_id = ?
        """, (customer_id,))

        customer = cursor.fetchone()

        if not customer:
            print("Customer not found.")
            return

        cursor.execute("""
            SELECT COUNT(*)
            FROM bookings
            WHERE customer_id = ?
        """, (customer_id,))

        booking_count = cursor.fetchone()[0]

        if booking_count > 0:
            print(
                "Cannot delete this customer because "
                "booking records exist."
            )
            return

        confirm = input(
            f"Delete customer {customer[0]}? (y/n): "
        )

        if confirm.lower() != "y":
            print("Deletion cancelled.")
            return

        cursor.execute("""
            DELETE FROM customers
            WHERE customer_id = ?
        """, (customer_id,))

        connection.commit()

        print("Customer deleted successfully!")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        connection.close()


def customer_menu():
    while True:
        print("\n===================================")
        print("        CUSTOMER MANAGEMENT")
        print("===================================")
        print("1. Add Customer")
        print("2. View Customers")
        print("3. Search Customer")
        print("4. Update Customer")
        print("5. Delete Customer")
        print("6. Back")
        print("===================================")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_customer()
        elif choice == "2":
            view_customers()
        elif choice == "3":
            search_customer()
        elif choice == "4":
            update_customer()
        elif choice == "5":
            delete_customer()
        elif choice == "6":
            break
        else:
            print("Invalid choice.")
