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
import boto3
import botocore
from scanp import scanflask


BUCKET_NAME = 'pe-inhanced-images'
KEY = 'test.jpg'
extension=KEY.rsplit('.', 1)[1]
s3 = boto3.resource('s3') 

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
        
        s3.Bucket(BUCKET_NAME).download_file(KEY, 'my_local_image1.'+extension)

        file='my_local_image1.jpg'
        name=file.rsplit('.', 1)[0]
        if name and allowed_file(file):
            originalFilename = file
            #file.save(os.path.join(app.config['UPLOAD_FOLDER'], originalFilename))
            path=app.config['UPLOAD_FOLDER']+'/'+originalFilename
            scanflask(file, app.static_url_path +'/scannedImages/', extension)

            stamp= str(int(time.time()))
            
            data1 = open(app.static_url_path + '/scannedImages/_clear.jpg', 'rb')
            key1 = 'clear'+stamp
            s3.Bucket('pe-inhanced-images').put_object(Key=key1+'.'+extension, Body=data1)    
            
            data2 = open(app.static_url_path + '/scannedImages/_scanned.jpg', 'rb')
            key2 = 'scanned'+stamp   
            s3.Bucket('pe-inhanced-images').put_object(Key=key2+'.'+extension, Body=data2)

            data3 = open(app.static_url_path + '/scannedImages/_inverted.jpg', 'rb')
            key3='inverted'+stamp   
            s3.Bucket('pe-inhanced-images').put_object(Key=key3+'.'+extension, Body=data3)


        
        '''
        file = request.files['file']
        if file and allowed_file(file.filename):
            originalFilename = file.filename
            uniqueFilename = str(int(time.time()))
            print (uniqueFilename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], originalFilename))
            path=app.config['UPLOAD_FOLDER']+'/'+originalFilename
            scanflask(path, uniqueFilename, app.static_url_path +'/scannedImages/')
        '''
        #else :


            
    return file
 
 
if __name__ == "__main__":
    
    app.run(debug=True, port=5000)    
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    session.init_app(app)

