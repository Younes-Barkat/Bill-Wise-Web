from flask import Flask, request
from flask import render_template

app = Flask(__name__)
app.secret_key = "bill_wise_app"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')



if __name__ == "__main__" :
    app.run(debug = True)