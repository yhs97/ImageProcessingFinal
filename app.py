from flask import Flask, flash, redirect, render_template, request, session, abort, send_from_directory
import time;
import os
from transformp.transform import four_point_transform
from skimage.filters import threshold_local
import numpy as np
import argparse
import cv2
import imutils
import sys
from scanp import scanflask
app = Flask(__name__,  static_url_path=os.path.dirname(os.path.realpath(__file__)))
app.secret_key = 'random string'

UPLOAD_FOLDER=app.static_url_path+'/uploads'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'jpe' , 'bmp', 'dib', 'jp2', 'webp', 'pgm', 'pbm', 'ppm', 'sr', 'ras', 'tiff', 'tif'])

app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

@app.route('/<path:path>')
def send_file(path):
    return send_from_directory(app.static_url_path +'/scannedImages' , path)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 

@app.route("/")
def index():
	return render_template("display.html")




@app.route("/convert" , methods=['POST'])
def convert():
    #if request.method == 'POST':
    #	if 'file' not in request.files:
    #        flash('No file part')
    filename = ""
    if request.method == 'POST':
        # check if the post request has the file part
        file = request.files['file']
        if file and allowed_file(file.filename):
            originalFilename = file.filename
            uniqueFilename = str(int(time.time()))
            print (uniqueFilename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], originalFilename))
            path=app.config['UPLOAD_FOLDER']+'/'+originalFilename
            scanflask(path, uniqueFilename, app.static_url_path +'/scannedImages/')
        
        #else :


            
    return uniqueFilename
 
 
if __name__ == "__main__":
    
    app.run(debug=True, port=4998)    
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    session.init_app(app)

