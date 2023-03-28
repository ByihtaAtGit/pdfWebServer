from flask import Flask, request, abort, Response, send_from_directory, jsonify
import requests
import os
from dotenv import load_dotenv
import datetime
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)

@app.route("/")
def hello_world():
    print(os.environ["DOWNLOAD_URI"])
    return 'Hello World', 200

@app.route('/pdf/<filename:string>', methods=['GET'])
def getPdf(filename):
    if request.method != "GET":
        abort(405)
    FILE_DIR = os.environ['DOWNLOAD_DIR_URI']
    file_name = secure_filename(filename)
    file_path = f"{FILE_DIR}/{file_name}"
    
    if not os.path.isfile(file_path):
        abort(404)
    
    #id = 0
    
    #bit_string = ""
    #base64_string = ""
    
    return send_from_directory(FILE_DIR, filename, as_attachment = True)
    
@app.route('/pdf', methods=['POST'])
def uploadPdf():
    if request.method != "POST":
        abort(405)
    
    BASE_URI = os.environ['UPLOAD_DIR_URI']
    file_l = sum(request.files.listvalues(), [])
    
    for file in file_l:
        filename = secure_filename(file.filename)
        file.save(f"{BASE_URI}/{filename}")
        
    return 'Done', 200
    
    
@app.route('/request', methods=['GET'])
def callPdf():
    if request.method != "GET":
        abort(405)
        
    BASE_URI = os.environ["BASE_URI"]
    DOWNLOAD_URI = os.environ['DOWNLOAD_URI']
    UPLOAD_URI = os.environ['UPLOAD_URI']
    NOTIFY_URI = os.environ['NOTIFY_URI']
    
        
    messageJson = {
        "task_id": 2,
        "download_uri": f"{BASE_URI}/{DOWNLOAD_URI}",
        "upload_uri": f"{BASE_URI}/{UPLOAD_URI}",
        "notify_uri": f"{BASE_URI}/{NOTIFY_URI}"
    }
    r = requests.get('http://127.0.0.1:5000/pdf')
    fileheaders = request.headers
    contentDisposition = fileheaders.get('Content-Disposition')
    print(f"ContentDisposition: {contentDisposition} \nType: {type(contentDisposition)}")
    #getFile = request.files[fileheaders]
    print(f"FileResponseHeaders: {fileheaders}")
    return 'Done', 200

@app.route('/notify')
def notify():
    t = datetime.datetime.now()
    tL = (t.year , t.month, t.day, t.hour, t.minute)
    message_json = request.get_json()
    NOTIFY_DIR_URI = os.environ['NOTIFY_DIR_URI']
    NOTIFY_FILENAME = os.environ['NOTIFY_FILENAME']
    
    with open(f"{NOTIFY_DIR_URI}/{NOTIFY_FILENAME}", 'a') as f:
        lineStr = ""
        headersL = ["year", "month", "day", "hour", "minute"] 
        for header, value in list(zip(headersL, tL)):
            lineStr += f"{str(header)}={value}" + "    "
        
        for key, value in message_json.items():
            lineStr +=  f"{str(key)}={value}" + "    "
        
        f.write(lineStr)
        
    return "Done", 200
