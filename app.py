from werkzeug.security import generate_password_hash,check_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
from flask import session  # Import the session module
from flask_mysqldb import MySQL
from datetime import datetime
import  traceback


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For flash messages
app.secret_key = 'your_secret_key'  # Add this line to your app setup

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # No password for root user
app.config['MYSQL_DB'] = 'hostel_management1'

mysql = MySQL(app)
@app.route("/")
def base():
    return render_template("base.html")

@app.route('/registration.html', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        # Get form data
        first_name = request.form['first_name']
        middle_name = request.form['middle_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        contact_number = request.form['contact_number']
        email = request.form['email']
        password = request.form['password']
        
        cur = mysql.connection.cursor()

        # Check if email already exists in the database
        cur.execute("SELECT * FROM registration WHERE email = %s", (email,))
        existing_user = cur.fetchone()
        if existing_user:
            flash('Email is already registered. Please log in.', 'danger')
            return redirect(url_for('user_login'))  # Redirect to user login page

        try:
            # Hash the password before storing
            hashed_password = generate_password_hash(password)

            # Insert data into MySQL
            cur.execute("INSERT INTO registration(first_name, middle_name, last_name, gender, contact_number, email, password) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                        (first_name, middle_name, last_name, gender, contact_number, email, hashed_password))
            mysql.connection.commit()
            cur.close()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('user_login'))  # Redirect to user login page

        except Exception as e:
            flash(f'Error: {e}', 'danger')
            return redirect(url_for('registration'))

    return render_template('registration.html')


@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Create a cursor to interact with the MySQL database
        cur = mysql.connection.cursor()

        # Query to find user by email
        cur.execute("SELECT * FROM registration WHERE email = %s", (email,))
        user = cur.fetchone()

        # Check if user exists and password is correct
        if user and check_password_hash(user[7], password):  # Assuming password is hashed and stored in the 7th column
            # Store the user's email in the session
            session['email'] = email

            # Redirect to user dashboard
            return redirect(url_for('user_dashboard'))
        else:
            # Invalid email or password
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('user_login'))

    return render_template('user_login.html')



ADMIN_EMAIL = 'admin12@gmail.com'
ADMIN_PASSWORD = 'admin'

@app.route('/admin_login.html', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Validate admin credentials
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True  # Set a session variable
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('admin_login.html')
@app.route("/admin_dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")

@app.route('/add_course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        # Get form data
        course_name = request.form['course_name']
        course_code = request.form['course_code']
        course_duration = request.form['course_duration']
        
        # Create a cursor
        cur = mysql.connection.cursor()
        
        # Insert the course data into the courses table
        cur.execute("INSERT INTO courses (course_name, course_code, course_duration) VALUES (%s, %s, %s)",
                    (course_name, course_code, course_duration))
        
        # Commit the changes
        mysql.connection.commit()
        
        # Close the cursor
        cur.close()
        
        # Flash a success message
        flash('Course added successfully!', 'success')
        
        # Redirect to the success page
        return redirect(url_for('success_add'))
    
    # If the method is GET, render the add_course form
    return render_template('add_course.html')
@app.route('/success_add')
def success_add():
    return render_template('success_add.html')  # Render the success page with the flash message

@app.route("/manage_course")
def manage_course():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, course_name, course_code, course_duration FROM courses")  # Adjust table columns if needed
    courses = cur.fetchall()
    cur.close()
    
    return render_template("manage_course.html", courses=courses)

# Function to get course by ID
def get_course_by_id(course_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM courses WHERE id = %s", [course_id])
        course = cur.fetchone()  # Fetch the course record based on ID
        cur.close()
        return course
    except Exception as e:
        print(f"Error fetching course: {e}")
        return None  # Return None if there is an error

# Route for deleting a course
@app.route("/delete_course/<int:course_id>", methods=["POST"])
def delete_course(course_id):
    try:
        # Create a cursor
        cur = mysql.connection.cursor()

        # Execute the query to delete the course from the courses table
        cur.execute("DELETE FROM courses WHERE id = %s", [course_id])

        # Commit the changes
        mysql.connection.commit()

        # Close the cursor
        cur.close()

        # Flash a success message
        flash("Course deleted successfully.", "success")

    except Exception as e:
        # If there's an error, flash the error message
        flash(f"Error deleting course: {e}", "danger")

    # Redirect back to the manage courses page
    return redirect(url_for("manage_course"))

@app.route("/manage_room")
def manage_room():
    try:
        # Fetch room data from the database
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM room")  # Replace "room" with your table name
        rooms = cursor.fetchall()  # Fetch all rows as a list of tuples
        cursor.close()

        # Pass room data to the template
        return render_template("manage_room.html", rooms=rooms)
    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/delete_room/<int:room_number>', methods=['POST'])  # Change to POST
def delete_room(room_number):
    try:
        # Delete the room from the database using room_number
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM room WHERE room_number = %s", (room_number,))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'success': True, 'message': 'Room deleted successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f"An error occurred: {str(e)}"})

@app.route('/update_room/<int:room_number>', methods=['GET', 'POST'])
def update_room(room_number):
    if request.method == 'GET':
        # Fetch the room details to pre-fill the form
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM room WHERE room_number = %s", (room_number,))
        room = cursor.fetchone()
        cursor.close()
        if room:
            return render_template('update_room.html', room=room)
        else:
            return f"Room with number {room_number} not found.", 404

    if request.method == 'POST':
        # Update the room in the database
        data = request.form
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                UPDATE room 
                SET room_type = %s, capacity = %s, 
                    per_day = %s, per_week = %s, per_month = %s, status = %s 
                WHERE room_number = %s
            """, (data['roomType'], data['capacity'], 
                  data['priceDay'], data['priceWeek'], data['priceMonth'], 
                  data['status'], room_number))
            mysql.connection.commit()
            cursor.close()
            return jsonify({'success': True, 'message': 'Room updated successfully!'})
        except Exception as e:
            return jsonify({'success': False, 'message': f"An error occurred: {str(e)}"})


@app.route('/add_room', methods=['GET', 'POST'])
def add_room():
    if request.method == 'POST':
        room_number = request.form['room_number']
        room_type = request.form['room_type']
        beds = request.form['beds']
        per_day = request.form['per_day']
        per_week = request.form['per_week']
        per_month = request.form['per_month']
        status = request.form['status']
        
        try:
            # Insert room data into the database
            cursor = mysql.connection.cursor()
            cursor.execute("""
                INSERT INTO room (room_number, room_type, capacity, per_day, per_week, per_month, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (room_number, room_type, beds, per_day, per_week, per_month, status))
            
            # Commit the changes to the database
            mysql.commit()
            
            # Return a JSON response to trigger the pop-up on the frontend
            return jsonify({'success': True, 'message': 'Room added successfully!'})
        
        except Exception as e:
            return jsonify({'success': False, 'message': f"An error occurred: {str(e)}"})

    return render_template('add_room.html')
@app.route("/student_registration", methods=['GET', 'POST'])
def student_registration():
    if request.method == 'POST':
        try:
            # Get form data and ensure valid integer input for fees and duration
            fees = request.form['fees']
            duration = request.form['duration']

            # Validate that 'fees' is a valid decimal and 'duration' is a valid integer
            if not fees.replace('.', '', 1).isdigit() or not duration.isdigit():
                raise ValueError("Fees must be a valid decimal number and Duration must be a valid integer.")
            
            fees = float(fees)  # Convert fees to float
            duration = int(duration)  # Convert duration to integer

            if fees <= 0 or duration <= 0:
                raise ValueError("Fees and Duration must be positive values.")
            
            # Other form data as usual
            room_number = request.form['room_number']
            seater = request.form['seater']
            food_status = request.form['food_status']
            stay_from = request.form['stay_from']
            room_type = request.form['room_type']
            course = request.form['course']
            first_name = request.form['first_name']
            middle_name = request.form.get('middle_name', '')  # Middle name is optional
            last_name = request.form['last_name']
            gender = request.form['gender']
            contact_no = request.form['contact_no']
            email = request.form['email']
            address = request.form['address']
            city = request.form['city']
            state = request.form['state']
            zip_code = request.form['zip']

            # SQL query to insert student data (excluding `id` since it's auto-increment)
            query = """
                INSERT INTO student_registration 
                (room_number, seater, fees, food_status, stay_from, duration, room_type, course, 
                first_name, middle_name, last_name, gender, contact_no, email, address, city, state, zip) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            """
            values = (room_number, seater, fees, food_status, stay_from, duration, room_type, course, 
                      first_name, middle_name, last_name, gender, contact_no, email, address, city, state, zip_code)

            # Debug: Check if the number of placeholders matches the number of values
            print(f"Number of placeholders: {query.count('%s')}")
            print(f"Number of values: {len(values)}")

            if query.count('%s') != len(values):
                raise ValueError("Mismatch between the number of placeholders and values.")
            
            # Execute query
            cursor = mysql.connection.cursor()
            cursor.execute(query, values)
            mysql.connection.commit()
            cursor.close()

            # Flash success message
            flash("Student registered successfully!", 'success')

            # Redirect to a success page or render the same page with a success message
            return render_template('student_registration.html')

        except ValueError as ve:
            flash(str(ve), 'danger')
        except Exception as e:
            flash(f'Error: {e}', 'danger')

    return render_template('student_registration.html')  # Render the student registration form in GET request



@app.route("/manage_student", methods=["GET", "POST"])
def manage_student():
    try:
        # Fetch all student data
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, first_name, middle_name, last_name, course, room_number FROM student_registration")
        students = cursor.fetchall()
        cursor.close()
        
        return render_template("manage_student.html", students=students)
    
    except Exception as e:
        return f"Error fetching data: {str(e)}", 500


@app.route("/update_student/<int:id>", methods=["GET", "POST"])
def update_student(id):
    if request.method == "POST":
        try:
            # Get updated data from the form
            first_name = request.form["first_name"]
            middle_name = request.form.get("middle_name", "")
            last_name = request.form["last_name"]
            course = request.form["course"]
            room_number = request.form["room_number"]

            # Update the student record
            cursor = mysql.connection.cursor()
            query = """
                UPDATE student_registration
                SET first_name = %s, middle_name = %s, last_name = %s, course = %s, room_number = %s
                WHERE id = %s
            """
            cursor.execute(query, (first_name, middle_name, last_name, course, room_number, id))
            mysql.connection.commit()
            cursor.close()
            flash("Student updated successfully!", "success")
            return redirect(url_for("manage_student"))
        
        except Exception as e:
            flash(f"Error updating student: {str(e)}", "danger")
            return redirect(url_for("manage_student"))

    # Fetch existing data for the selected student
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, first_name, middle_name, last_name, course, room_number FROM student_registration WHERE id = %s", (id,))
    student = cursor.fetchone()
    cursor.close()
    return render_template("update_student.html", student=student)


@app.route("/delete_student/<int:id>", methods=["POST"])
def delete_student(id):
    try:
        # Delete the student record
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM student_registration WHERE id = %s", (id,))
        mysql.connection.commit()
        cursor.close()
        flash("Student deleted successfully!", "success")
        return redirect(url_for("manage_student"))
    
    except Exception as e:
        flash(f"Error deleting student: {str(e)}", "danger")
        return redirect(url_for("manage_student"))

@app.route('/new_complaint')
def new_complaint():
    cur = mysql.connection.cursor()
    try:
        cur.execute('SELECT * FROM complaints')
        complaints = cur.fetchall()
        print("Fetched complaints:", complaints)  # This will log the complaints in your Flask logs
        cur.close()
    except Exception as e:
        print(f"Error fetching complaints: {e}")
        complaints = []

    return render_template('new_complaint.html', complaints_data=complaints)


@app.route("/closed_complaint")
def closed_complaint():
    
    cur = mysql.connection.cursor()
    try:
        cur.execute('SELECT * FROM complaints')
        complaints = cur.fetchall()
        print("Fetched complaints:", complaints)  # This will log the complaints in your Flask logs
        cur.close()
    except Exception as e:
        print(f"Error fetching complaints: {e}")
        complaints = []

    return render_template('closed_complaint.html', complaints_data=complaints)

@app.route("/inprocess_complaint")
def inprocess_complaint():
    cur = mysql.connection.cursor()
    try:
        cur.execute('SELECT * FROM complaints')  # Ensure this table name is correct
        complaints = cur.fetchall()
        print("Fetched complaints:", complaints)  # This will log the complaints in your Flask logs
        cur.close()
    except Exception as e:
        print(f"Error fetching complaints: {e}")
        complaints = []

    return render_template('inprocess_complaint.html', in_process_complaints=complaints)  # Corrected variable name

@app.route("/change_status", methods=["POST"])
def change_status():
    complaint_id = request.form["complaint_id"]
    status = request.form["status"]

    cursor = mysql.connection.cursor()

    if status == "closed":
        # Move the complaint to the closed_complaint table
        cursor.execute("""
            INSERT INTO closed_complaint (id, name, email, subject, category, message, status, created_at)
            SELECT id, name, email, subject, category, message, 'closed', created_at FROM complaints WHERE id = %s
        """, (complaint_id,))
        
        # Delete the complaint from the complaints table
        cursor.execute("DELETE FROM complaints WHERE id = %s", (complaint_id,))
    
    elif status == "in-process":
        # Move the complaint to the inprocess_complaint table
        cursor.execute("""
            INSERT INTO inprocess_complaint (id, name, email, subject, category, message, status, created_at)
            SELECT id, name, email, subject, category, message, 'in process', created_at FROM complaints WHERE id = %s
        """, (complaint_id,))
        
        # Delete the complaint from the complaints table
        cursor.execute("DELETE FROM complaints WHERE id = %s", (complaint_id,))
    
    # Commit the changes
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for("new_complaint"))

@app.route("/remove_complaint", methods=["POST"])
def remove_complaint():
    complaint_id = request.form['complaint_id']
    conn = mysql.connection.cursor()
    conn.execute('DELETE FROM complaints WHERE id = ?', (complaint_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('new_complaint'))

@app.route("/view_feedback")
def view_feedback():
    # Fetch the feedback data from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, feedback_type, feedback_message, email, submitted_at FROM feedback")
    feedback_data = cur.fetchall()  # Fetch all rows
    
    # Close the cursor
    cur.close()

    # Pass the data to the template
    return render_template("view_feedback.html", feedback_data=feedback_data)

# Route for user access
@app.route("/user_access")
def user_access():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id,last_name, email,registration_date FROM registration")  # Adjust table columns if needed      # Fetch all records from the registration table
    users = cur.fetchall()
    cur.close()
    
    return render_template("user_access.html", users=users)

# Function to get user by ID
def get_user_by_id(user_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM registration WHERE id = %s", [user_id])
        user = cur.fetchone()  # Fetch the user record based on ID
        cur.close()
        return user
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None  # Return None if there is an error

# Route for deleting a user
@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM registration WHERE id = %s", [user_id])
    mysql.connection.commit()
    cur.close()
    
    flash("User deleted successfully.", "success")
    return redirect(url_for("user_access"))

# Route to view user details
@app.route('/view_user/<int:user_id>')
def view_user(user_id):
    user = get_user_by_id(user_id)  # Fetch the user details by user_id
    if user:
        return render_template('view_user.html', user=user)  # Render the user details in a template
    else:
        return "User not found", 404  # Handle case where user is not found


@app.route("/user_dashboard")
def user_dashboard():
    if 'email' not in session:
        flash('Please log in first.', 'danger')
        return redirect(url_for('user_login'))
    
    return render_template("user_dashboard.html")



@app.route('/book_hostel', methods=['GET', 'POST'])
def book_hostel():
    if request.method == 'POST':
        try:
            # Capture form data
            room_no = request.form.get('room_no', '').strip()
            seater = request.form.get('seater', '').strip()
            fees = request.form.get('fees', '').strip()
            food_status = request.form.get('foodStatus', '').strip()
            stay_from = request.form.get('stayfrom', '').strip()
            stay_duration = request.form.get('stayDuration', '').strip()
            course = request.form.get('course', '').strip()
            first_name = request.form.get('firstName', '').strip()
            middle_name = request.form.get('middelName', '').strip()
            last_name = request.form.get('lastName', '').strip()
            gender = request.form.get('gender', '').strip()
            phone = request.form.get('phone', '').strip()
            email = request.form.get('email', '').strip()
            guardian_name = request.form.get('guardianName', '').strip()
            guardian_relation = request.form.get('guardianRelation', '').strip()
            guardian_contact_no = request.form.get('guardianContactNo', '').strip()
            address = request.form.get('address', '').strip()
            city = request.form.get('city', '').strip()
            state = request.form.get('state', '').strip()

            # Validate numeric fields
            fees = float(fees) if fees else 0
            seater = int(seater) if seater else 0
            stay_duration = int(stay_duration) if stay_duration else 0

            # Check for missing fields
            required_fields = [
                room_no, seater, fees, food_status, stay_from, stay_duration, course,
                first_name, last_name, gender, phone, email, guardian_name,
                guardian_relation, guardian_contact_no, address, city, state
            ]
            if not all(required_fields):
                return "All fields are required."

            # Insert into database
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO book_hostel (
                    room_no, seater, fees, food_status, stay_from, stay_duration, course,
                    first_name, middle_name, last_name, gender, phone, email,
                    guardian_name, guardian_relation, guardian_contact_no, address, city, state
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                room_no, seater, fees, food_status, stay_from, stay_duration, course,
                first_name, middle_name, last_name, gender, phone, email,
                guardian_name, guardian_relation, guardian_contact_no, address, city, state
            ))
            mysql.connection.commit()
            cur.close()

            # Redirect to success page
            return redirect(url_for('success'))

        except Exception as e:
            return f"An error occurred: {e}"

    return render_template('book_hostel.html')  # Assuming your form is in a template named `book_hostel_form.html`
@app.route('/success')
def success():
    return render_template('success.html')

@app.route("/complaint", methods=["GET","POST"])
def complaint():
       if request.method == 'POST':
        try:
            # Retrieve form data
            name = request.form['name']
            email = request.form['email']
            subject = request.form['subject']
            category = request.form['category']
            message = request.form['message']

            # Insert into database
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO complaints (name, email, subject, category, message)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, email, subject, category, message))
            mysql.connection.commit()
            cur.close()

            # Provide feedback to the user
            flash('Complaint registered successfully!', 'success')
            return redirect(url_for('success_complaint'))
        except Exception as e:
            flash(f'An error occurred: {e}', 'danger')
            return redirect(url_for('complaint'))
       return render_template('complaint.html')  # Update with your HTML file name

@app.route('/success_complaint')
def success_complaint():
    return render_template('success_complaint.html')

@app.route("/registered_complaint")
def registered_complaint():
    # Check if the user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    user_id = session['user_id']  # Get the logged-in user's ID

    try:
        # Connect to the database and fetch complaints
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT complaint_number, complaint_type, status, reg_date 
            FROM complaints 
            WHERE user_id = %s
        """, (user_id,))
        complaints = cur.fetchall()  # Fetch all complaints for the user
        cur.close()  # Close the cursor

        # Render the complaints on the template
        return render_template('registered_complaint.html', complaints=complaints)

    except Exception as e:
        print(f"Error: {e}")
        return "An internal server error occurred.", 500



@app.route("/feedback")
def feedback():
    return render_template("feedback.html")

# Route to handle the form submission
@app.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    # Retrieve the data from the form
    feedback_type = request.form.get("feedbackType")
    feedback_message = request.form.get("feedbackMessage")
    email = request.form.get("email")
    
    # Create a cursor to execute the query
    cur = mysql.connection.cursor()

    # Insert the feedback data into the database
    cur.execute("""
    INSERT INTO feedback (feedback_type, feedback_message, email)
    VALUES (%s, %s, %s)
""", (feedback_type, feedback_message, email))


    # Commit the changes to the database
    mysql.connection.commit()

    # Close the cursor
    cur.close()

    # Print the data for debugging
    print(f"Feedback Type: {feedback_type}")
    print(f"Message: {feedback_message}")
    print(f"Email: {email}")
    
    # After processing, redirect the user to a thank-you page
    return redirect(url_for("thank_you"))

# Route for the thank-you page after feedback is submitted
@app.route("/thank_you")
def thank_you():
    return render_template("thank_you.html")

@app.route('/user_profile', methods=['GET', 'POST'])
def user_profile():
    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.form['firstName']
            middle_name = request.form.get('middleName', '')
            last_name = request.form['lastName']
            gender = request.form['gender']
            contact_number = request.form['contactNumber']
            email = request.form['email']

            # Insert data into the database
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO user_profiles (first_name, middle_name, last_name, gender, contact_number, email)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (first_name, middle_name, last_name, gender, contact_number, email))
            mysql.connection.commit()
            cur.close()

            # Provide feedback to the user
            flash('Profile submitted successfully!', 'success')
            return redirect(url_for('success_user_profile'))
        except Exception as e:
            flash(f'An error occurred: {e}', 'danger')
            return redirect(url_for('user_profile'))

    return render_template('user_profile.html')

@app.route('/success_profile')
def success_user_profile():
    return render_template('success_user_profile.html')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    # Check if the user is logged in
    if 'email' not in session:  
        flash('You need to log in first.', 'danger')
        return redirect(url_for('user_login'))  # Redirect to login if not logged in

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # Check if new passwords match
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('change_password'))  # Stay on the page if there's an error
        
        # Check if current password is correct
        cur = mysql.connection.cursor()
        cur.execute("SELECT password FROM users WHERE email = %s", (session['email'],))
        user = cur.fetchone()

        # If user is found and the current password matches
        if user and check_password_hash(user[0], current_password):  # Assuming the first column is the password
            # Hash the new password and update the database
            hashed_new_password = generate_password_hash(new_password)
            try:
                cur.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_new_password, session['email']))
                mysql.connection.commit()
                flash('Password updated successfully!', 'success')
                return redirect(url_for('user_dashboard'))  # Redirect to the dashboard
            except Exception as e:
                flash(f"Error updating password: {str(e)}", 'danger')  # Catch any exceptions and show error
                return redirect(url_for('change_password'))
        else:
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('change_password'))  # Stay on the page if the password is incorrect

    # If it's a GET request, render the form
    return render_template('change_password.html')

@app.route('/room_detail') 
def room_detail():
    try:
        cursor = mysql.connection.cursor()
        # Fetch all room details from the database
        cursor.execute("SELECT * FROM room")
        rooms = cursor.fetchall()  # Fetch all rows from the query
        cursor.close()

        return render_template('room_detail.html', rooms=rooms)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route('/book_room', methods=['POST'])
def book_room():
    data = request.get_json()
    room_number = data.get('room_number')
    
    try:
        cursor = mysql.connection.cursor()
        # Update the status of the room to 'Booked'
        cursor.execute("UPDATE room SET status = 'Booked' WHERE room_number = %s AND status = 'Available'", (room_number,))
        
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': f'Room {room_number} is already booked or does not exist.'})
        
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': f'Room {room_number} booked successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred while booking the room.', 'error': str(e)})


@app.route('/access_log')
def access_log():
    try:
        db = mysql.connection
        cursor = db.cursor()

        # Query to fetch data from the `registration` table
        cursor.execute("SELECT id, last_name, registration_date FROM registration")
        logs = cursor.fetchall()  # Fetch all rows

        # Render the template with the logs
        return render_template('access_log.html', access_logs=logs)
    except Exception as e:
        print("Error:", traceback.format_exc())
        return "An error occurred while processing your request.", 500

@app.route('/clear_access_log', methods=['POST'])
def clear_access_log():
    try:
        # Clear the `registration` table
        db = mysql.connection
        cursor = db.cursor()
        cursor.execute("DELETE FROM registration")
        db.commit()
        return jsonify({"message": "Access log cleared successfully"}), 200
    except Exception as e:
        # Log the error and return an error response
        print("Error:", traceback.format_exc())
        return jsonify({"message": "Failed to clear access log"}), 500

@app.route('/delete_access_log/<int:log_id>', methods=['POST'])
def delete_access_log(log_id):
    try:
        print(f"Deleting log with ID: {log_id}")  # Debugging line
        db = mysql.connection
        cursor = db.cursor()
        cursor.execute("DELETE FROM registration WHERE id = %s", (log_id,))
        db.commit()
        return jsonify({"message": "Log entry deleted successfully"}), 200
    except Exception as e:
        print("Error:", traceback.format_exc())
        return jsonify({"message": "Failed to delete log entry"}), 500


if __name__ == '__main__':
    app.run(debug=True)
