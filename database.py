import mariadb


def get_connection():
    try:
        connection = mariadb.connect(
            host="localhost",
            user="vehicle_app",
            password="Vehicle@123",
            database="vehicle_management"
        )

        return connection

    except mariadb.Error as e:
        print(f"Database connection error: {e}")
        return None
