from database import get_connection

from modules.vehicle import vehicle_menu
from modules.customer import customer_menu
from modules.booking import booking_menu
from modules.billing import billing_menu


def main():

    connection = get_connection()

    if connection is None:
        print("Could not connect to database.")
        return

    connection.close()

    while True:

        print("\n")
        print("=" * 45)
        print("       VEHICLE MANAGEMENT SYSTEM")
        print("=" * 45)
        print("1. Vehicle Management")
        print("2. Customer Management")
        print("3. Booking")
        print("4. Billing")
        print("5. Exit")
        print("=" * 45)

        choice = input("Enter your choice: ")

        if choice == "1":
            vehicle_menu()

        elif choice == "2":
            customer_menu()

        elif choice == "3":
            booking_menu()

        elif choice == "4":
            billing_menu()

        elif choice == "5":
            print("\nThank you for using the system!")
            break

        else:
            print("\nInvalid choice. Please try again.")


if __name__ == "__main__":
    main()
