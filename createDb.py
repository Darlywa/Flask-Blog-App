import mysql.connector

myDb = mysql.connector.connect(host="localhost",
                               port = "8051",
                               user="root",
                               passwd="password123",
                               )
my_cursor = myDb.cursor()
my_cursor.execute("CREATE DATABASE our_users")

my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
    print(db)