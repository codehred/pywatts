from flask import Flask, render_template, redirect, request, session
import hashlib

app = Flask(__name__)
app.secret_key = 'dev'


VALID_USERNAME = 'user'
VALID_PASSWORD_HASH = hashlib.sha256('pass'.encode()).hexdigest()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if username == VALID_USERNAME and password_hash == VALID_PASSWORD_HASH:
            session['user'] = username
            return redirect('/dashboard')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    if request.method == 'POST':
        device = request.form['device']
        power = request.form['power']
        hours = request.form['hours']
        energy_consumed = float(power) * float(hours)
        print(device, energy_consumed)

    return render_template('dashboard.html', username=session['user'])

if __name__ == '__main__':
    app.run(debug=True)