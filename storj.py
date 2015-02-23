import logging
import requests
import io
import struct
import binascii
import functools

token=""
NODE_URL="http://node1.metadisk.org"

def upload(path,data):
    byteio=io.BytesIO(data)
    r = requests.post(NODE_URL+'/api/upload', files={'file':(path,byteio)},
            data={'token':token})
    j=r.json()
    logging.debug('filehash='+j['filehash']+' key='+j['key'])
    return (binascii.unhexlify(j['filehash']),[binascii.unhexlify(j['key'])])

#@functools.lru_cache(maxsize=512)
def download(hash,key):
    hash=str(binascii.hexlify(hash),'ascii')
    key=str(binascii.hexlify(key[0]),'ascii')
    r = requests.get(NODE_URL+'/api/download/'+hash+'?key='+key)
    return r.content

def delete(hash):
    pass

#logging.basicConfig(filename='metafuse.log',level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

r = requests.post(NODE_URL+'/accounts/token/new')
token=r.json()['token']
logging.debug('token='+token)
