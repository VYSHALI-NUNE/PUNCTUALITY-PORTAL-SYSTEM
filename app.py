from flask import Flask, request, render_template, jsonify
import mysql.connector
from datetime import datetime
from twilio.rest import Client

app = Flask(__name__)

# Twilio Configuration
account_sid = ''        #give your twilio account sid
auth_token = ''         #give your twilio authentication token
twilio_client = Client(account_sid, auth_token)

# MySQL Connection
db = mysql.connector.connect(
    host="localhost",
    user="",                  #give your database username
    password="",              # Replace with your MySQL password
    database=""               #give your database name
 )
cursor = db.cursor(dictionary=True)

# Standard class start time
CLASS_START_TIME = "09:00:00"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/mark-attendance', methods=['POST'])
def mark_attendance():
    data = request.form
    student_id = data['student_id']
    
    # Determine which time input to use
    if data['arrival_time']:  # Manual input
        arrival_time_str = data['arrival_time']
    else:  # Time picker input
        arrival_time_str = data['time_picker']

    # Convert to datetime objects
    arrival_time = datetime.strptime(arrival_time_str, '%H:%M:%S')
    class_start_time = datetime.strptime(CLASS_START_TIME, '%H:%M:%S')

    # Check if the student is late
    if arrival_time > class_start_time:
        late_by = arrival_time - class_start_time
        cursor.execute('SELECT * FROM student WHERE id = %s', (student_id,))
        student = cursor.fetchone()

        if student:
            message_body = (
                f"Dear {student['parent_name']}, your child {student['name']} "
                f"was late to class on {datetime.now().date()} by {late_by}."
            )
            try:
                # Send SMS via Twilio
                message = twilio_client.messages.create(
                    body=message_body,
                    from_='+13233065903',  # Your Twilio phone number
                    to=student['parent_phone']  # Ensure this field exists in your database
                )
                return jsonify({"message": "SMS sent successfully", "sid": message.sid}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        else:
            return jsonify({"error": "Student not found"}), 404
    else:
        return jsonify({"message": "Student is on time"}), 200

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

