from flask import Flask, flash, redirect, render_template, request, session, abort, send_from_directory, jsonify
import time;
import os
from transformp.transform import four_point_transform
from skimage.filters import threshold_local
import numpy as np
import argparse
import json
import cv2
import imutils
import sys
import boto3
import requests
import botocore
from urlparse import urlparse
from scanp import scanflask
from flask_cors import CORS


BUCKET_NAME = 'pe-inhanced-images'
#KEY = 'test.jpg'
#extension=KEY.rsplit('.', 1)[1]

s3 = boto3.resource('s3') 

app = Flask(__name__,  static_url_path=os.path.dirname(os.path.realpath(__file__)))
app.secret_key = 'random string'
CORS(app)

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




@app.route("/convert" , methods=['GET'])
def convert():
    #if request.method == 'POST':
    #	if 'file' not in request.files:
    #        flash('No file part')
    filename = ""
    if request.method == 'GET':
        # check if the post request has the file part
        imageUrl = request.args['img_src'];
        print imageUrl
        ext=imageUrl.rsplit('.')
        length = len(ext)
        extension = ext[length-1]    
        print extension
        o = urlparse(imageUrl)
        
        bucketName = o.netloc.rsplit('.s3',1)[0]
        KEY=o.path
        KEY=KEY[1:]
        print KEY
        print bucketName
        downloadedFileName = 'local_image.'
        downloadedFileName = downloadedFileName+extension


        try:
            s3.Bucket(bucketName).download_file(KEY, downloadedFileName)
        except:
            newBucketName=KEY.rsplit('/',1)[0]
            s3.Bucket(newBucketName).download_file(KEY, downloadedFileName)

        file = 'local_image.'+extension
        name = file.rsplit('.', 1)[0]
        if name and allowed_file(file):
            originalFilename = file
            #file.save(os.path.join(app.config['UPLOAD_FOLDER'], originalFilename))
            path = app.config['UPLOAD_FOLDER']+'/'+originalFilename
            scanflask(file, app.static_url_path +'/scannedImages/', extension)

            s3c = boto3.client('s3' ,region_name='ap-southeast-1')
            
            stamp = str(int(time.time()))
            
            data1 = open(app.static_url_path + '/scannedImages/_clear.'+extension, 'rb')
            key = 'clear'+stamp+'.'+extension
            s3.Bucket('pe-inhanced-images').put_object(Key=key, Body=data1)   

            url = s3c.generate_presigned_url(ClientMethod='get_object',Params={'Bucket': 'pe-inhanced-images','Key': key,},                                  
                                            ExpiresIn=600)
            # data2 = open(app.static_url_path + '/scannedImages/_scanned.'+extension, 'rb')
            # key2 = 'scanned'+stamp   
            # s3.Bucket('pe-inhanced-images').put_object(Key=key2+'.'+extension, Body=data2)

            # data3 = open(app.static_url_path + '/scannedImages/_inverted.'+extension, 'rb')
            # key3='inverted'+stamp   
            # s3.Bucket('pe-inhanced-images').put_object(Key=key3+'.'+extension, Body=data3)
             

        
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
    return json.dumps({'url': url}), 200, {'Content-Type':'application/json'} 
             
 
if __name__ == "__main__":
    
    app.run(debug=True, port=5000)    
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    session.init_app(app)

