from flask import Flask, request
from flask import render_template
import settings
import utils

app = Flask(__name__)
app.secret_key = "bill_wise_app"

billscan = utils.BillScan()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['image_name']
        up_img_path = utils.save_up_img(file)
        print('image saved in', up_img_path)
        four_points, size = billscan.bill_scanner(up_img_path)
        print(four_points, size)
        
        return render_template('scanner.html')
    
    return render_template('scanner.html')
@app.route('/about')
def about():
    return render_template('about.html')



if __name__ == "__main__" :
    app.run(debug = True)