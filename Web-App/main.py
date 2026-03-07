from flask import Flask, request

app = Flask(__name__)
app.secret_key = "bill_wise_app"

@app.route('/')
def index():
    return "bill wise"



if __name__ == "__main__" :
    app.run(debug = True)