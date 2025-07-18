from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # flash 메시지 사용 시 필요

# Handle static file requests from HTML
@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('static', filename)

@app.route('/static/assets/<path:filename>')
def serve_static_assets(filename):
    return send_from_directory('static', filename)

# Page routes
@app.route('/')
@app.route('/index.html')
def home():
    return render_template('index.html')

@app.route('/about')
@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/chart')
@app.route('/chart.html')
def chart():
    return render_template('chart.html')

@app.route('/roadmap')
@app.route('/roadmap.html')
def roadmap():
    return render_template('roadmap.html')

@app.route('/login')
@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/signup')
@app.route('/signup.html')
def signup():
    return render_template('signup.html')

@app.route('/find_password')
@app.route('/find_password.html')
def find_password():
    return render_template('findPassword.html')

@app.route('/test')
def test():
    return render_template('test.html')

if __name__ == '__main__':
    app.run(debug=True)