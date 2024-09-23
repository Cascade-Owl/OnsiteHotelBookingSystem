from datetime import datetime, timedelta
from mysql.connector.pooling import MySQLConnectionPool
from mysql.connector import Error
import time

def main():

    print("Welcome to the hotel booking system!")
    time.sleep(0.5)


    while True:
        print("Please enter the MySQL database credentials!")
        print()

        try:
            #Collect MySQL Database Credentials
            db_user = input("User: ")
            db_pass = input("Password: ")
            db_host = input("Host: ")
            db_name = input("Name of the database to be used: ")
            db_port = int(input("Port: "))

            dbconfig = {
                "user" : db_user,
                "password" : db_pass,
                "host" : db_host,
                "database" : db_name,
                "port" : db_port
            }
        
        except ValueError:
            print("Please input integers only on the database port credential!")
            continue

        print()

        try:
            #Create connection pool
            print("Connecting to the database...")
            time.sleep(0.5)
            pool = MySQLConnectionPool(pool_name='pool_a', pool_size=3, **dbconfig)
            print()
            print("Connected to the database successfully!")
            break

        except Error as err:
            print("Error code: ", err.errno)
            print("Error message: ", err.msg)
            print()

    connection = pool.get_connection()
    cursor = connection.cursor()

    #Initalize the database and trigger
    initialize_database(cursor, connection)
    initialize_notify_trigger(cursor, connection)

    #Queue for booked customers with no vacant room
    customer_queue = []

    #Main menu
    while True:
        print()

        print("""
Please choose a course of action:
1. Add Customer
2. Delete Customer
3. Show All Past Room Appointements 
4. Refresh
5. Exit
        """)
        
        print()

        try:
            input_choice = int(input("Choice [1/2/3/4/5]: "))
        except ValueError:
            print("Error, Please input 1 and 2 only!")
            continue

        match input_choice:
            case 1:
                AddCustomer(customer_queue, cursor, connection)
            case 2:
                DeleteCustomer(customer_queue, cursor, connection)
            case 3:
                ShowNotifications(cursor)
            case 4:
                continue
            case 5:
                break
            case _:
                print("Error, something went wrong...")

        AutomateCustomerLeave(cursor, connection)
        AutomateQueue(customer_queue, cursor, connection)
    
def initialize_database(cursor, connection):
    #Create the booking system database if it does not exist
    print("Initializing database...")

    print("Creating MyDBHotel_Customers table...")
    cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS MyDBHotel_Customers (
        CustomerID INT NOT NULL AUTO_INCREMENT,
        CustomerName VARCHAR(255) NOT NULL,
        PRIMARY KEY (CustomerID)
    ) ENGINE = InnoDB;
    """)
    connection.commit()


    print("Creating MyDBHotel_Bookings table...")
    cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS MyDBHotel_Bookings (
        BookingID INT NOT NULL AUTO_INCREMENT,
        CustomerID INT NOT NULL,
        BookingDateTime DATETIME NOT NULL,
        PRIMARY KEY (BookingID),
        INDEX customer_id_fk_idx (CustomerID ASC),
        CONSTRAINT customer_id_fk
            FOREIGN KEY (CustomerID)
            REFERENCES MyDBHotel_Customers (CustomerID)
            ON DELETE NO ACTION
            ON UPDATE NO ACTION
    ) ENGINE = InnoDB;
    """)
    connection.commit()


    print("Creating MyDBHotel_Rooms table...")
    cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS MyDBHotel_Rooms (
        RoomID INT NOT NULL,
        BookingID INT NULL,
        LeaveDateTime DATETIME NULL,
        PRIMARY KEY (RoomID),
        INDEX booking_id_fk_idx (BookingID ASC),
        CONSTRAINT booking_id_fk
            FOREIGN KEY (BookingID)
            REFERENCES MyDBHotel_Bookings (BookingID)
            ON DELETE NO ACTION
            ON UPDATE NO ACTION
    ) ENGINE = InnoDB;
    """)

    connection.commit()

    print("Creating MYDBHotel_Notifications table...")
    cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS MYDBHotel_Notifications (
        NotificationID INT NOT NULL AUTO_INCREMENT,
        BookingsStatusMessage VARCHAR(999) NOT NULL,
        PRIMARY KEY (NotificationID)
    ) ENGINE = InnoDB;
    """)

    connection.commit()

    #Initialize room size to 5
    cursor.execute("SELECT COUNT(*) FROM MyDBHotel_Rooms")
    room_count = cursor.fetchone()[0]
    if room_count == 0:
        for i in range(1, 6):
            cursor.execute(f"""
                INSERT INTO MyDBHotel_Rooms (RoomID)
                VALUES ({i});
                        """)
        
        connection.commit()

    print("Database initialization complete!")

def initialize_notify_trigger(cursor, connection):
    #Create MySQL trigger for storing room occupation history
    
    cursor.execute("DROP TRIGGER IF EXISTS NotifyOccupiedRoom;")
    connection.commit()
    
    cursor.execute("""
        CREATE TRIGGER NotifyOccupiedRoom
        AFTER UPDATE ON MyDBHotel_Rooms
        FOR EACH ROW
        BEGIN
            IF NEW.BookingID IS NOT NULL THEN
                INSERT INTO MYDBHotel_Notifications (BookingsStatusMessage)
                VALUES (
                    CONCAT(
                        (SELECT CustomerName FROM MyDBHotel_Customers WHERE CustomerID = 
                        (SELECT CustomerID FROM MyDBHotel_Bookings WHERE BookingID = NEW.BookingID)),
                        ' has been booked at room ', NEW.RoomID
                        )
                    );
            END IF;
        END;
        """)
    connection.commit()

def AddCustomer(queue, cursor, connection):
    #Add and book a customer
    customer_name = input("Name of the customer to add: ")
    print()
    
    cursor.execute(""" 
    INSERT INTO MyDBHotel_Customers (CustomerName)
    VALUES (%s);
    """, (customer_name,))

    connection.commit()

    cursor.execute(""" 
    SELECT CustomerID 
    FROM MyDBHotel_Customers 
    WHERE CustomerName = %s 
    ORDER BY CustomerID DESC LIMIT 1;
    """, (customer_name,))

    customer_id = cursor.fetchone()[0]
    print(f"Customer {customer_name} Added with ID {customer_id}!")

    print()

    print(f"Booking customer {customer_name}...")

    current_time = datetime.now()
    leave_time = current_time + timedelta(minutes=1, seconds=25)
    
    formatted_current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    formatted_leave_time = leave_time.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(""" 
    INSERT INTO MyDBHotel_Bookings (CustomerID, BookingDateTime)
    VALUES (%s, %s);
    """, (customer_id, formatted_current_time))
   
    connection.commit()

    cursor.execute(""" 
    SELECT BookingID 
    FROM MyDBHotel_Bookings 
    WHERE CustomerID = %s 
    ORDER BY BookingDateTime DESC LIMIT 1;
    """, (customer_id,))

    booking_id = cursor.fetchone()[0]

    cursor.execute("""
    SELECT RoomID 
    FROM MyDBHotel_Rooms
    WHERE BookingID IS NULL AND LeaveDateTime IS NULL;     
                   """)
    
    results = cursor.fetchall()

    #Queue the customer if there are no rooms available
    if not results:
        queue.append(customer_name)
        print(f"{customer_name} is queued due to lack of vacant rooms.")
        print(f"There are {queue.index(customer_name)} waiting customers in line before {customer_name}.")

        cursor.execute("""
        SELECT LeaveDateTime
        FROM MyDBHotel_Rooms
        ORDER BY LeaveDateTime ASC
        LIMIT 1;
                       """)
        
        results = cursor.fetchall()

        print(f"The next vacant room will be at {results[0][0]}")

    #Appoint the customer a room if there are rooms available
    else:

        for row in results:
            cursor.execute("""
            UPDATE MyDBHotel_Rooms         
            SET BookingID = %s, LeaveDateTime = %s
            WHERE RoomID = %s  
            """, (booking_id, formatted_leave_time, row[0]))
            break
        
        print(f"Customer {customer_name} is assigned at room {row[0]}, with a leave time of {formatted_leave_time}")

def DeleteCustomer(queue, cursor, connection):
    #Delete all records of the customer in the database and removes them as occupant of a room if they are a room occupant
   
    customer_name = input("Name of the customer to delete: ")

    print("Deleting customer...")
    print("Cancelling booking...")

    cursor.execute("""
    SELECT CustomerID
    FROM MyDBHotel_Customers
    WHERE CustomerName = %s
    """, (customer_name,))
    
    results = cursor.fetchall()

    #Print if customer name does not exists
    if not results:
        print("Customer does not exists!")
        return
    
    #Delete all associated records if customer name exists
    else:
        customer_id = results[0][0]

        cursor.execute("""
        SELECT BookingID
        FROM MyDBHotel_Bookings
        WHERE CustomerID = %s
        """, (customer_id,))
        
        booking_results = cursor.fetchall()

        if booking_results:
            booking_id = booking_results[0][0]

            cursor.execute("""
            UPDATE MyDBHotel_Rooms
            SET BookingID = NULL, LeaveDateTime = NULL
            WHERE BookingID = %s;
            """, (booking_id,))
            connection.commit()

            cursor.execute("""
            DELETE FROM MyDBHotel_Bookings
            WHERE CustomerID = %s;
            """, (customer_id,))
            connection.commit()

        cursor.execute("""
        DELETE FROM MyDBHotel_Customers
        WHERE CustomerID = %s;
        """, (customer_id,))
        connection.commit()

        if customer_name in queue:
            queue.remove(customer_name)

        print(f"Customer {customer_name} is deleted!")

def AutomateCustomerLeave(cursor, connection):
    #Remove an occupant of a room if LeaveDateTime is equal or behind the current time
    cursor.execute("""
    SELECT LeaveDateTime
    FROM MyDBHotel_Rooms
    WHERE LeaveDateTime IS NOT NULL;
                   """)
    
    results = cursor.fetchall()

    current_time = datetime.now()

    for row in results:
        leave_time = row[0]

        if leave_time <= current_time:
            cursor.execute("""
            UPDATE MyDBHotel_Rooms
            SET BookingID = NULL, LeaveDateTime = NULL
            WHERE LeaveDateTime = %s
            """, (row[0],))

            connection.commit()

            print(f"A customer left! A new room is vacant!")

def AutomateQueue(queue, cursor, connection):  
    #Add a queued customer once a vacant room is detected
    if queue:  
        for customer in queue[:]:
            cursor.execute("""
            SELECT RoomID
            FROM MyDBHotel_Rooms
            WHERE BookingID IS NULL AND LeaveDateTime IS NULL;             
                        """)
            
            results = cursor.fetchall()

            if results:
                current_time = datetime.now()
                leave_time = current_time + timedelta(minutes=1, seconds=25)
                
                formatted_leave_time = leave_time.strftime("%Y-%m-%d %H:%M:%S")

                RoomID = results[0][0]

                cursor.execute("""
                UPDATE MyDBHotel_Rooms 
                SET BookingID = (SELECT BookingID FROM MyDBHotel_Bookings WHERE CustomerID = 
                                (SELECT CustomerID FROM MyDBHotel_Customers WHERE CustomerName = %s)), 
                                LeaveDateTime = %s
                WHERE RoomID = %s;
                                """, (customer, formatted_leave_time, RoomID))
                
                connection.commit()

                print(f"Customer {customer} has been added at Room {RoomID} with a leave time of {formatted_leave_time}")

                queue.remove(customer)

            else:
                print(f"No vacant rooms available for {customer} at the moment.")

    if not queue:
        return    

def ShowNotifications(cursor):
    #Print records associated with room occupation history
    cursor.execute("""
    SELECT BookingsStatusMessage 
    FROM MYDBHotel_Notifications
    ORDER BY NotificationID DESC;
    """)

    results = cursor.fetchall()

    if results:
        for row in results:
            print(row[0])

if __name__ == "__main__":
    main()

