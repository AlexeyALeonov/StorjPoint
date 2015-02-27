# coding: utf-8

from flask import Flask,request,make_response,send_file,Response
import StorjFS
import DAVXml
from functools import wraps
import urllib.request
import re
import logging

app = Flask(__name__)
host='192.168.1.22'
port=80
root="root"
fs=StorjFS.StorjFS()
xml=DAVXml.DAVXml(host,root,fs)

def __withException(func):
    @wraps(func)
    def wrapper(path):
        try:
            path = re.sub(r'^'+root, '', path)
            path=urllib.parse.unquote(path,encoding='utf-8')
            return func(path)
        except FileNotFoundError:
            return '',404
        except PermissionError:
            return '',403
    return wrapper



@app.route('/', defaults={'path': ''},methods=['OPTIONS'])
@app.route('/<path:path>',methods=['OPTIONS'])
def options(path):
    response = make_response()
    response.headers['Allow'] =\
        'GET, POST, DELETE, PROPPATCH, MOVE, MKCOL, COPY, PROPFIND'
    response.headers['DAV']='1'
    return response

@app.route('/', defaults={'path': ''},methods=['PROPFIND'])
@app.route('/<path:path>',methods=['PROPFIND'])
@__withException
def propfind(path):
    depth=request.headers.get('Depth')
    return xml.propfind(path,depth),207

@app.route('/', defaults={'path': ''},methods=['PROPPATCH'])
@app.route('/<path:path>',methods=['PROPPATCH'])
@__withException
def proppatch(path):
    return xml.proppatch(path,request.data),207

@app.route('/', defaults={'path': ''},methods=['MKCOL'])
@app.route('/<path:path>',methods=['MKCOL'])
@__withException
def mkcol(path):
    fs.createDir(path)
    return '',201

@app.route('/', defaults={'path': ''},methods=['COPY'])
@app.route('/<path:path>',methods=['COPY'])
@__withException
def copy(path):
    pass

@app.route('/', defaults={'path': ''},methods=['MOVE'])
@app.route('/<path:path>',methods=['MOVE'])
@__withException
def move(path):
    dest=request.headers.get('Destination')
    dest = re.sub(r'^http://'+host+'/'+root, '', dest)
    dest=urllib.parse.unquote(dest,encoding='utf-8')
    overwrite=request.headers.get('Overwrite')=='T'
    try:
        fs.move(path,dest,overwrite)
    except FileExistsError:
        return '',412
    return '',201

@app.route('/', defaults={'path': ''},methods=['GET'])
@app.route('/<path:path>',methods=['GET'])
@__withException
def get(path):
    print(request.headers)
    size=fs.getBlob(path).size
    def generate():
        total=0
        with fs.readFile(path) as f:
            while total<size:
                byte = f.read(512)
                if byte=='':
                    time.sleep(5)
                else:
                    total=total+len(byte)
                    yield byte
 
    return Response(generate())

@app.route('/', defaults={'path': ''},methods=['UNLOCK'])
@app.route('/<path:path>',methods=['UNLOCK'])
@__withException
def unlock(path):
    print(request.data)
    return '',204

@app.route('/', defaults={'path': ''},methods=['LOCK'])
@app.route('/<path:path>',methods=['LOCK'])
@__withException
def lock(path):
    print(request.data)
    return xml.lock(path,request.data),207

@app.route('/', defaults={'path': ''},methods=['HEAD'])
@app.route('/<path:path>',methods=['HEAD'])
@__withException
def head(path):
    pass

@app.route('/', defaults={'path': ''},methods=['POST'])
@app.route('/<path:path>',methods=['POST'])
@__withException
def post(path):
    existFile=fs.updateFile(path,request.data)
    if existFile:
        return '',204
    else:
        return '',201

@app.route('/', defaults={'path': ''},methods=['PUT'])
@app.route('/<path:path>',methods=['PUT'])
@__withException
def put(path):
    existFile=fs.updateFile(path,request.data)
    if existFile:
        return '',204
    else:
        return '',201

app.route('/', defaults={'path': ''},methods=['DELETE'])
@app.route('/<path:path>',methods=['DELETE'])
@__withException
def delete(path):
    fs.unlink(path)
    return '',204

def start():
    app.run(host=host,port=port,debug=True,threaded=True)


