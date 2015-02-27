# coding: utf-8

import logging
import requests
import io
import struct
import binascii
import urllib.request

token=""
NODE_URL="http://node1.metadisk.org"

def uploadFile(path,file):
    path=urllib.parse.quote(path,encoding='utf-8')
    r = requests.post(NODE_URL+'/api/upload', files={'file':(path,file)},
            data={'token':token})
    j=r.json()
    logging.debug('uploaded to storj:filehash='+j['filehash']+' key='+j['key'])
    return (j['filehash'],j['key'])

def upload(path,data):
    byteio=io.BytesIO(data)
    return uploadFile(path,byteio)

def download(hash,key,chunk_size=1*1024):
    r = requests.get(NODE_URL+'/api/download/'+hash+'?key='+key,stream=True)
    if r.status_code!=requests.codes.ok:
        logging.critical('cannot download '+hash)
        raise FileNotFoundError()
    return r.iter_content(chunk_size=chunk_size)

def delete(hash):
    pass

r = requests.post(NODE_URL+'/accounts/token/new')
token=r.json()['token']
logging.debug('token='+token)
