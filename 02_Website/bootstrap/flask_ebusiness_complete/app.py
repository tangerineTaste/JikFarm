from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio-details.html')

@app.route('/service')
def service():
    return render_template('service-details.html')

if __name__ == '__main__':
    app.run(debug=True)
