# coding: utf-8

import logging
import threading
import hashlib
import os
import storj
import time
import BlobTree

tmpdir='tmp/'
maxSize=100*1024*1024

class Cache:
    def __init__(self,fs):
        self.fs=fs
        self.size=0
        self.lru=[]
        self.blobs=[]
        self.lockFS=lock = threading.Lock()
        t=threading.Thread(target=self.__uploadFS).start()
        t=threading.Thread(target=self.__uploadBlob).start()

    def __uploadFS(self):
        while True:
            if self.fs.dirty:
                logging.info('uploading filesystem root')
                with self.lockFS:
                    self.fs.save()
                logging.info('uploaded filesystem root')
            time.sleep(1*60)

    def __uploadBlob(self):
        while True:
            while len(self.blobs)>0:
                d=self.blobs.pop(0)
                if d.counter>0:
                    logging.info('uploading blob:'+d.hash)
                    (hash,passwords)=\
                         storj.uploadFile('dummy.dat',open(tmpdir+d.hash,'rb'))
                    logging.info('uploaded blob:'+d.hash)
                    with self.lockFS:
                        d.hash=hash
                        d.passwords=passwords
                        self.fs.dirty=True
            time.sleep(10)

    def load(self,blob):
        path=tmpdir+blob.hash
        if blob.hash not in self.lru:
            self.lru.insert(0,blob.hash)
            def __load():
                try:
                   with open(path,'wb') as f:
                        for cont in storj.download(blob.hash,blob.passwords):
                            f.write(cont)
                except FileNotFoundError:
                    logging.critical(blob.hash+' is broken')
            threading.Thread(target=__load).start()
        else:
            self.lru.remove(blob.hash)
            self.lru.insert(0,blob.hash)

        while not os.access(path,os.F_OK):
            time.sleep(5)

        return open(path,'rb')

    def save(self,blob,data):
        s=hashlib.sha256()
        s.update(data)
        hash=s.hexdigest()
        blob.hash=hash
        if blob not in self.blobs:
            self.blobs.append(blob)
        if hash not in self.lru:
            self.size=self.size+len(data)
            self.lru.insert(0,hash)
            with open(tmpdir+hash,'wb') as f:
                f.write(data)
            while(self.size>maxSize):
                h=self.lru[len(self.lru)+1]
                self.size=self.size-os.stat(tmpdir+h).st_size
                os.remove(tmpdir+h)
                self.lru.remove(h)

        


