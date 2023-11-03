from flask import Flask, render_template #load the Flask module into your Python script
import mariadb #load mariadb module into python script
import mysql.connector as database #Used for database connection
import sys

try:
    connection = database.connect(
        user="test",
        password="test",
        host="192.168.1.18",
        port=3306,
        database="measurements")
    print("Connected to database")
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

app = Flask(__name__) #create a Flask object called app:
cursor = connection.cursor()

@app.route('/')
def datadraw():
    cursor.execute("SELECT * FROM ITtek")
    ITdata = cursor.fetchall()
    cursor.execute("SELECT * FROM service")
    Servicedata = cursor.fetchall()
    return render_template('index.html', ITtek=ITdata, service=Servicedata)

app.run(debug =True, host='0.0.0.0', port=5000)
#app.run(debug =True)