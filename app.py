from flask import Flask, render_template, request, redirect, session, jsonify
import json, os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

DATA_FILE = 'data.json'
USER_FILE = 'users.json'

# -------- DATA --------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"vehicles": []}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# -------- USERS --------
def load_users():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)

# -------- REGISTER --------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()

        for u in users:
            if u['username'] == username:
                return render_template('register.html', error="User exists")

        users.append({
            "username": username,
            "password": generate_password_hash(password)
        })

        save_users(users)
        return redirect('/')

    return render_template('register.html')

# -------- LOGIN --------
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()

        for u in users:
            if u['username'] == username and check_password_hash(u['password'], password):
                session['user'] = username
                return redirect('/dashboard')

        return render_template('login.html', error="Invalid login")

    return render_template('login.html')

# -------- DASHBOARD --------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    return render_template('index.html')

# -------- LOGOUT --------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# -------- API --------
@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    return jsonify(load_data()['vehicles'])

@app.route('/api/vehicles', methods=['POST'])
def add_vehicle():
    data = load_data()
    v = request.json
    v['id'] = len(data['vehicles']) + 1
    data['vehicles'].append(v)
    save_data(data)
    return jsonify(v)

@app.route('/api/vehicles/<int:id>', methods=['PUT'])
def update_vehicle(id):
    data = load_data()
    updated = request.json

    for i, v in enumerate(data['vehicles']):
        if v['id'] == id:
            updated['id'] = id
            data['vehicles'][i] = updated
            save_data(data)
            return jsonify(updated)

    return jsonify({'error': 'Not found'}), 404

@app.route('/api/vehicles/<int:id>', methods=['DELETE'])
def delete_vehicle(id):
    data = load_data()
    data['vehicles'] = [v for v in data['vehicles'] if v['id'] != id]
    save_data(data)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)