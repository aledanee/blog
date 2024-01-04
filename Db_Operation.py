
import mysql.connector


def connect_to_mysql(host, username, password, database):
    try:
        # Establish a connection to the MySQL server
        connection = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=database
        )

        if connection.is_connected():
            print("Connected to MySQL database")

            # Return the connection object for further use
            return connection

    except Exception as e:
        print(f"Error: {str(e)}")



