import pyrebase
import os
from flask import Flask, render_template,request, url_for, jsonify, redirect, session, g, url_for
# from flask_session import Session
from flask_dropzone import Dropzone
from fastai.vision.all import *



import pathlib
from io import BytesIO

import os
import PIL

import numpy as np

config = {
    "apiKey": "AIzaSyBVVQ2OHuNlqR0jh2iegHnw8pqYZqFyJhc",
    "authDomain": "mlimageclassdemo.firebaseapp.com",
    "databaseURL": "",
    "projectId": "mlimageclassdemo",
    "storageBucket": "mlimageclassdemo.appspot.com",
    "messagingSenderId": "113589091191",
    "appId": "1:113589091191:web:ed4f319cfc6ac90b417f72"
}



app = Flask(__name__)

app.secret_key = os.urandom(24)
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

# app.secret_key = 'key'
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

user_loggedin = False

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

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def upload():
    global user_loggedin
    user_loggedin = False
    
    try:
        print(session['usr'])
        return redirect(url_for('home'))
    except KeyError:
        if request.method == "POST":
            email = request.form['name']
            password = request.form['password']
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                user = auth.refresh(user['refreshToken'])
                user_id = user['idToken']
                session['usr'] = user_id
                return redirect(url_for('home'))
            except:
                unsuccessful = 'Login Failed, Please check your credentials'
                message = "Incorrect Password!"
                return render_template('index.html', umessage=unsuccessful)
        return render_template('index.html', umessage='')    

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if (request.method == 'POST'):
            email = request.form['name']
            password = request.form['password']
            auth.create_user_with_email_and_password(email, password)
            return render_template('index.html')
    return render_template('create_account.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if (request.method == 'POST'):
            email = request.form['name']
            auth.send_password_reset_email(email)
            return render_template('index.html')
    return render_template('forgot_password.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    try:
        print(session['usr'])
        return render_template("home.html")
    except KeyError:
        return redirect(url_for('upload'))
    # return render_template('home.html')
    

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
    return render_template('layout.html', loggedin=logdetls)

@app.route('/hse-demo', methods=['POST', 'GET'])    
def hseDemo():
    global filename
    
    global data
    global labels
    global md_type

    global pred
    global predidx
    global prob
    global user_loggedin

    md_type = 'hse'
    file = None

    try:
        print(session['usr'])
        if request.method == 'POST':

            # if user_loggedin != True:
            #     return render_template('index.html')

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
        # return render_template("hse-demo.html")
    except KeyError:
        return redirect(url_for('upload'))

    # print('yum yum.............*****************')
    # print(user_loggedin)
    

@app.route('/drill-bit-demo', methods=['POST', 'GET'])   
def drillBitDemo():
    global filename
    
    global data
    global labels
    global md_type

    global pred
    global predidx
    global prob
    global user_loggedin

    md_type = 'drill'
    
    file = None
    try:
        print(session['usr'])
        if request.method == 'POST':

            if user_loggedin != True:
                return render_template('index.html')

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
    except KeyError:
        return redirect(url_for('upload'))    

# if __name__ == '__main__':
#     app.debug = True
#     app.run()

if  __name__ == '__main__':
    app.run(host="0.0.0.0")