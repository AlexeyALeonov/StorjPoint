# coding: utf-8

from flask import Flask,request,make_response
import StorjFS
import DAVXml
from functools import wraps

app = Flask(__name__)
host='192.168.1.22'
port=80
root="root"
fs=StorjFS.StorjFS()
xml=DAVXml.DAVXml(host,root,fs)

def __withException(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            return '',404
        except PermissionError:
            return '',403
#        except Exception as e:
#            print(e)
#            return '',500
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
    path.replace(root,'')
    fs.crateDir(path)
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
    dest.replace(root,'')
    overwrite=request.headers.get('Overwrite')
    path.replace(root,'')
    try:
        fs.move(path,dest,overwrite=='T')
    except FileExistsError:
        return '',412
    return '',201

@app.route('/', defaults={'path': ''},methods=['GET'])
@app.route('/<path:path>',methods=['GET'])
@__withException
def get(path):
    path.replace(root,'')
    return fs.readFile(path),200


@app.route('/', defaults={'path': ''},methods=['HEAD'])
@app.route('/<path:path>',methods=['HEAD'])
@__withException
def head(path):
    pass

@app.route('/', defaults={'path': ''},methods=['POST'])
@app.route('/<path:path>',methods=['POST'])
@__withException
def post(path):
    path.replace(root,'')
    return fs.updateFile(path,request.data),200

@app.route('/', defaults={'path': ''},methods=['PUT'])
@app.route('/<path:path>',methods=['PUT'])
@__withException
def put(path):
    path.replace(root,'')
    return fs.updateFile(path,request.data),200

app.route('/', defaults={'path': ''},methods=['DELETE'])
@app.route('/<path:path>',methods=['DELETE'])
@__withException
def delete(path):
    path.replace(root,'')
    fs.unlink(path)
    return '',204


app.run(host=host,port=port,debug=True)
