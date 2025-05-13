from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from utils.shell_ops import create_user, delete_user, list_users, get_inactive_users, get_gpu_stats  # Import get_inactive_users

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for session

# Login Page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            session['logged_in'] = True
            return redirect(url_for('display'))  # Redirect to the display page
        else:
            return render_template('login.html', error='Invalid Credentials')
    return render_template('login.html')

# Dashboard Page
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# List Users Page
@app.route('/search_user', methods=['GET', 'POST'])
def search_user_route():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        search_query = request.form.get('search_query', '').strip()
        success, users_or_error = list_users()
        if success:
            # Filter users based on the search query
            filtered_users = [user for user in users_or_error if search_query.lower() in user.lower()]
            return render_template('search_user.html', users=filtered_users, query=search_query)
        else:
            return render_template('search_user.html', error=users_or_error)
    
    # For GET requests, display all users
    success, users_or_error = list_users()
    if success:
        return render_template('search_user.html', users=users_or_error)
    else:
        return render_template('search_user.html', error=users_or_error)

# Create User Form Page
@app.route('/create_user', methods=['GET', 'POST'])
def create_user_route():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        room = request.form['room']
        workphone = request.form['workphone']
        homephone = request.form['homephone']
        other = request.form['other']

        success, message = create_user(username, password, fullname, room, workphone, homephone, other)
        return render_template('create_user.html', success=success, message=message)
    return render_template('create_user.html')

# Delete User Form Page
@app.route('/delete_user', methods=['GET', 'POST'])
def delete_user_route():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        username = request.form['username']
        success, message = delete_user(username)  # Call the delete_user function
        return render_template('delete_user.html', success=success, message=message)
    return render_template('delete_user.html')

# List Users Page
@app.route('/list_users')
def list_users_route():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    success, users_or_error = list_users()
    if success:
        return render_template('list_users.html', users=users_or_error)
    else:
        return render_template('list_users.html', error=users_or_error)

# Add a new route for the display page
@app.route('/display')
def display():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('display.html')

# Add a new route for the server utilization dashboard
@app.route('/server_dashboard')
def server_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Example stats data (replace this with actual data from your backend logic)
    stats = {
        "system": {
            "platform": "Linux",
            "platform_release": "5.15.0-70-generic",
            "platform_version": "#77-Ubuntu SMP",
            "architecture": "x86_64",
            "hostname": "server-host",
            "processor": "Intel(R) Xeon(R) CPU",
            "uptime": "2 days, 4:32:10"
        },
        "cpu": {
            "physical_cores": 4,
            "total_cores": 8,
            "total_usage": 45.3,
            "usage_per_core": [40.5, 50.2, 42.1, 48.3, 43.7, 47.8, 44.9, 46.5]
        },
        "memory": {
            "total": "16 GB",
            "available": "8 GB",
            "used": "8 GB",
            "percentage": "50%"
        },
        "disk": [
            {
                "mountpoint": "/",
                "device": "/dev/sda1",
                "filesystem_type": "ext4",
                "total_size": "500 GB",
                "used": "200 GB",
                "percentage": "40%",
                "free": "300 GB"
            }
        ],
        "network": {
            "total_bytes_sent": "1.2 GB",
            "total_bytes_received": "3.4 GB"
        }
    }

    # Pass the stats variable to the template
    return render_template('serverdashboard.html', stats=stats)

# Add a new route for inactive users
@app.route('/inactive_users')
def inactive_users_route():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    success, users_or_error = get_inactive_users(days=30)  # Check for users inactive for 30 days
    if success:
        return render_template('inactive_users.html', users=users_or_error)
    else:
        return render_template('inactive_users.html', error=users_or_error)

@app.route('/api/gpu_stats')
def gpu_stats():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    success, gpu_data = get_gpu_stats()
    if success:
        return jsonify(gpu_data)
    else:
        return jsonify({"error": gpu_data}), 500

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
