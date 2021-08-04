import os
from flask import Flask, render_template,request, url_for, jsonify
from flask_dropzone import Dropzone
from fastai.vision.all import *

import pathlib
from io import BytesIO

import os
import PIL

import numpy as np




app = Flask(__name__)
app.secret_key = 'key'

plt = platform.system()
if plt == 'Windows': pathlib.PosixPath = pathlib.WindowsPath

dir_path = os.path.dirname(os.path.realpath(__file__))

temp = pathlib.PosixPath
# pathlib.PosixPath = pathlib.WindowsPath
path = Path()
path.ls(file_exts='.pkl')

app.config.update(
    UPLOADED_PATH=os.path.join(dir_path, 'static/uploads'),
    # Flask-Dropzone config:
    DROPZONE_ALLOWED_FILE_TYPE='image',
    DROPZONE_MAX_FILE_SIZE=3,
    DROPZONE_MAX_FILES=20
)
app.config['DROPZONE_REDIRECT_VIEW'] = 'analyseImage'

dropzone = Dropzone(app)

filename = None



def prepare_image(img):
    img = Image.open(img)
    # img = PILImage.create(img)
    img = img.resize((240, 240))
    img = np.array(img)
    #img = np.expand_dims(img, 0)
    return img

def plot_probability_histogram(probability):
    x = np.arange(len(probability))
    plt.bar(x, probability)
    labels = ['boot', 'gloves', 'hard hat', 'road cones', 'vest', 'weld mask']
    plt.xticks(x, labels)
    plt.show()
    
def predict_image(img, img_type):
    if img_type == 'hse':
        hse_model = load_learner('deep_hse_model.pkl')
    elif img_type == 'drill':
        hse_model = load_learner('drilling_bit_model.pkl')

    prediction, prediction_idx, probability = hse_model.predict(img)
    return prediction, prediction_idx, probability

def infer_image():
    global filename
    
    # file = request.files.get('file')
    print("The file path....")
    print(filename)
    file = filename
    img_bytes = file.read()
    img = prepare_image(img_bytes)
    prediction, prediction_idx, probability = predict_image(img, 'hse')
    return jsonify(prediction, str(probability[prediction_idx]))    


@app.route('/', methods=['POST', 'GET'])
def upload():
            
    return render_template('index.html')

@app.route('/analyse_image', methods=['POST', 'GET'])
def analyseImage():
    global filename
    
    global data
    global labels
    global md_type

    global pred
    global predidx
    global prob

    modelType = ""

    # imageres = infer_image()
    print("The image is...")
    print(filename)
    filename = 'uploads/' + filename

    if md_type == 'hse':
        modelType = "(Model Results - HSE)"
    elif modelType == 'drill':
        modelType = "(Model Results - Drill Bit)"

    
    return render_template("analyse_image.html", file_name = filename, data = data, labels = labels, title= modelType, pred = pred, predidx = predidx, prob = prob)

@app.route('/layout')    
def layout():
    return render_template('layout.html')

@app.route('/hse-demo', methods=['POST', 'GET'])    
def hseDemo():
    global filename
    
    global data
    global labels
    global md_type

    global pred
    global predidx
    global prob
    
    md_type = 'hse'
    file = None
    if request.method == 'POST':

        dir = os.path.join(app.config['UPLOADED_PATH'],"") 
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))

        f = request.files.get('file')
        file = f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
        print("The file .......:::::")
        print(type(f.read()))

        print("The file path....")
        print(dir)

        print("The file path2....")
        print(file)

        
        # img_bytes = f.read()
        img = prepare_image(f)
        prediction, prediction_idx, probability = predict_image(img, md_type)

        pred = prediction
        predidx = prediction_idx.tolist()
        prob = probability.tolist()

        print("The Predictions .......:::::")
        print(pred,  predidx, prob)
       
        data = probability.tolist()         
        labels = ['boot', 'gloves', 'hard hat', 'road cones', 'vest', 'weld mask']

        filename = f.filename
    return render_template('hse-demo.html', title="(HSE)")    

@app.route('/drill-bit-demo', methods=['POST', 'GET'])   
def drillBitDemo():
    global filename
    
    global data
    global labels
    global md_type

    global pred
    global predidx
    global prob

    md_type = 'drill'
    
    file = None
    if request.method == 'POST':

        dir = os.path.join(app.config['UPLOADED_PATH'],"") 
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))

        f = request.files.get('file')
        file = f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
        print("The file .......:::::")
        print(type(f.read()))

        print("The file path....")
        print(dir)

        print("The file path2....")
        print(file)

        
        # img_bytes = f.read()
        img = prepare_image(f)
        prediction, prediction_idx, probability = predict_image(img, md_type)

        pred = prediction
        predidx = prediction_idx.tolist()
        prob = probability.tolist()

        print("The Predictions .......:::::")
        print(pred,  predidx, prob)
       
        data = probability.tolist()         
        labels = ['Drilling bit', 'Not drilling bit']

        filename = f.filename
    return render_template('drill-bit-demo.html', title="(Drill-bit)")        

if  __name__ == '__main__':
    port = int(os.environ.get('PORT', 2000))
    app.run(host="0.0.0.0", port = port)