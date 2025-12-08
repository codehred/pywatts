from flask import Flask, render_template, redirect, request, session

app = Flask(__name__)
app.secret_key = 'dev'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        if username:
            session['username'] = username
            return redirect('/dashboard')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/')
    if request.method == 'POST':
        device = request.form['device']
        power = request.form['power']
        hours = request.form['hours']
        energy_consumed = float(power) * float(hours)
        print(device, energy_consumed)

    return render_template('dashboard.html', username=session['username'])

if __name__ == '__main__':
    app.run(debug=True)