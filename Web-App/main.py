from flask import Flask, request
from flask import render_template
import settings
import cv2
import utils
import predictions as pred
import numpy as np

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
        if four_points is None:
            message = 'UNABLE TO DETECT THE COORDINATES OF THE DOCUMENT'
            points = [
                {'x':10, 'y':10},
                {'x':120, 'y':10},
                {'x':120, 'y':120},
                {'x':10, 'y':120},
            ]
            return render_template('scanner.html', points=points, fileupload=True, message=message)
        
        else:
            points = utils.array2json(four_points)
            message = 'LOACATED THE COORDINATES OF THE DOCUMENT '
            return render_template('scanner.html', points=points, fileupload=True, message=message)

        
        return render_template('scanner.html')
    
    return render_template('scanner.html')

@app.route('/transform', methods=['POST'])
def transform():
    try:
        points = request.json['data']
        array = np.array(points)
        fixed_img = billscan.calibrate(array)
        filename = 'fixed_img.jpg'
        fixed_img_path = settings.join_path(settings.MEDIA_DIR, filename)
        cv2.imwrite(fixed_img_path, fixed_img)
        return 'successed'
    except:
        return 'failed'
    
@app.route('/prediction')
def prediction():
    wrap_img = settings.join_path(settings.MEDIA_DIR, 'fixed_img.jpg')
    image = cv2.imread(wrap_img)
    img_bb, results = pred.get_predictions(image)
    bb_filename = settings.join_path(settings.MEDIA_DIR, 'BoundingBox.jpg')
    cv2.imwrite(bb_filename, img_bb)
    return render_template('predictions.html', results = results)



@app.route('/about')
def about():
    return render_template('about.html')



if __name__ == "__main__" :
    app.run(debug = True)