####### IMPORTS #######
import mariadb
import paho.mqtt.client as mqtt
import mysql.connector as database
import sys

####### CONNECTING TO DATABASE #######
try:
    connection = database.connect(
        user="test",
        password="test",
        host="192.168.1.18",
        port=3306,
        database="measurements")
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)


####### DATABASE CURSOR #######
# a cursor is a database object that retrieves
# and also updates data, one row at a time,
# from a set of data.
cursor = connection.cursor()


####### ADD DATA to database tabeller: ITtek & service#######
def add_data_to_ITtek(datetime, client_id, client_ip, broker):
    try:
        statement = "INSERT INTO ITtek (datetime, client_id, client_ip, broker) VALUES (%s, %s, %s, %s)"
        data = (datetime, client_id, client_ip, broker)
        cursor.execute(statement, data)
        connection.commit()
        print("Successfully added entry to table ITtek")
    except database.Error as e:
        print(f"Error adding entry to table ITtek: {e}")


def add_data_to_service(datetime, client_id, userinput):
    try:
        statement = "INSERT INTO service (datetime, client_id, userinput) VALUES (%s, %s, %s)"
        data = (datetime, client_id, userinput)
        cursor.execute(statement, data)
        connection.commit()
        print("Successfully added entry to table service")
    except database.Error as e:
        print(f"Error adding entry to table service: {e}")

####### RETRIEVE DATA from database #######
# Using the same execute() method on the database cursor, you can retrieve a database entry.
def get_data_from_ITtek(client_id):
    try:
        statement = "SELECT * FROM ITtek WHERE client_id=%s"
        data = (client_id,)
        cursor.execute(statement, data)
        for (datetime, client_id, client_ip, broker) in cursor:
            print(
                f"Successfully retrieved {datetime}, {client_id}, {client_ip}, {broker}")
    except database.Error as e:
        print(f"Error retrieving entry from database: {e}")
def get_data_from_service(client_id):
    try:
        statement = "SELECT * FROM service WHERE client_id=%s"
        data = (client_id,)
        cursor.execute(statement, data)
        for (datetime, client_id, userinput) in cursor:
            print(f"Successfully retrieved {datetime}, {client_id}, {userinput}")
    except database.Error as e:
        print(f"Error retrieving entry from database: {e}")

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("iot/status/klient_1")
    client.subscribe("iot/klient_1")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

    data = msg.payload.decode('utf-8').split(" | ")
    datetime = data[0]
    client_id = data[1]
    client_ip = data[2]
    broker = data[3]
    userinput = data[4]
    #ap_SSID = data[4]
    #ap_mac = data[5]
    #ap_signal = data[6]

    ### ADD DATA TO DATABASE ###
    add_data_to_service(datetime, client_id, userinput)
    add_data_to_ITtek(datetime, client_id, client_ip, broker)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.1.18", 1883, 60)
client.loop_forever()


### RETRIEVE DATA FROM DATABASE ###
# get_data_from_service("klient_1")
# get_data_from_ITtek("klient_1")

####### CLOSE CONNECTION #######
# connection.close()


### TUTORIAL ###
# https://www.digitalocean.com/community/tutorials/how-to-store-and-retrieve-data-in-mariadb-using-python-on-ubuntu-18-04

