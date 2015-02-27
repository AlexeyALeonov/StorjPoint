# coding: utf-8

import time
import logging
import json
import io
import bz2

from BlobTree import Blob 
from BlobTree import Tree 
import storj
import Cache

class StorjFS:
    def __init__(self):
        self.dirty=False
        self.cache=Cache.Cache(self)
        try:
            with open('storjfs.json') as f:
                data = json.load(f)
            d=b''
            for cont in storj.download(data['hash'],data['key']):
                d=d+cont
            data=str(bz2.decompress(d),'ascii')
            self.load(data)
        except FileNotFoundError:
            self.root=Tree(0o755)
            self.dirty=True

    def save(self):
        data=bz2.compress(bytes(self.dump(),'utf-8'))
        dump={'name':'root'}
        (dump['hash'],dump['key'])=storj.upload("storjfs.dat",data)
        with open('storjfs.json','w') as f:
            json.dump(dump,f)
        self.dirty=False

    def load(self,jtext):
        blobs={}
        trees=[]
        objs=json.loads(jtext)
        for obj in objs:
            if obj['type']=='tree':
                tree=Tree.fromJson(obj)
                trees.append(tree)
                blobs[obj['no']]=tree
            if obj['type']=='blob':
                blob=Blob.fromJson(obj)
                blobs[obj['no']]=blob
        for t in trees:
            for k,v in t.files.items():
                t.files[k]=blobs[v]
        self.root=blobs[0]
 
    def __downloadByBlob(self,blob):
        if blob.isDir():
            raise IsADirectoryError()
        if not blob.isReadable():
            raise PermissionError()
        return self.cache.load(blob)

    def __searchParentTree(self,path):
        if path=='/':
            return (self.root,None)
        dirs=path.split('/')
        while '' in dirs:
            dirs.remove('')
        tree=self.root
        for p in dirs[0:-1]:
            if p not in tree.files:
                raise FileNotFoundError()
            tree=tree.files[p]
            if not tree.isDir():
                raise FileNotFoundError()
        return (tree,dirs[len(dirs)-1])

    def __getFilename(self,path):
        dirs=path.split('/')
        return dirs[len(dirs)-1]

    def __deleteFromStorj(self,blob):
        if blob.counter==0 and not blob.isDir():
            storj.delete(blob.hash)
        
    def getBlob(self,path):
        (parent,name)=self.__searchParentTree(path)
        if name==None:
            blob=parent
        else:
            if name not in parent.files:
                raise FileNotFoundError()
            blob=parent.files[name]
        blob.updateAtime()
        return blob

    def hardlink(self,fromm,to):
        (parrent,name)=self.__searchParentTree(to)
        toDir=parent.file[name]
        if not toDir.isDir():
            raise PermissionError()
        (parent,name)=self.__searchParentTree(fromm)
        fromBlob=parent[name]
        if fromBlob==None:
            raise FileNotFoundError()
        with self.cache.lockFS:
            toDir.addFile(name,fromBlob)
            self.dirty=True

    def setPermission(self,path,permission):
        with self.cache.lockFS:
            self.getBlob(path).setPermission(permission)
            self.dirty=True

    def updateFile(self,path,data,permission=0o755):
        (parent,name)=self.__searchParentTree(path)
        existFile=False
        with self.cache.lockFS:
            if name in parent.files:
                existFile=True
                pre=parent.files[name]
                permission=pre.permission
                self.__deleteFromStorj(pre)
                parent.unlink(name)
            blob=Blob('',len(data),permission,'')
            parent.addFile(name,blob)
            self.cache.save(blob,data)
            self.dirty=True
        return existFile
 
    def createDir(self,path,permission=0o755):
        (parent,name)=self.__searchParentTree(path)
        tree=Tree(permission,parent)
        with self.cache.lockFS:
            parent.addFile(name,tree)
            self.dirty=True

    def readFile(self,path):
        blob=self.getBlob(path)
        if blob.isDir():
            raise IsADirectoryError()
        return self.__downloadByBlob(blob)

    def readDir(self,path):
        tree=self.getBlob(path)
        if not tree.isDir():
            raise NotADirectoryError()
        if not tree.isExecutable():
            raise PermissionError()
        return tree.files

    def unlink(self,path):
        (parent,name)=self.__searchParentTree(path)
        with self.cache.lockFS:
            blob=parent.unlink(name)
            self.__deleteFromStorj(blob)
            self.dirty=True


    def move(self,fromm,dest,overwrite=True):
        (destParent,destName)=self.__searchParentTree(dest)
        with self.cache.lockFS:
            if destName in destParent.files:
                if not overwite:
                    raise FileExistsError()
                blob=destParent.unlink(destName)
                self.__deleteFromStorj(blob)
            (fromParent,fromName)=self.__searchParentTree(fromm)
            destParent.addFile(destName,fromParent.files[fromName])
            fromParent.unlink(fromName)
            self.dirty=True

    def __listBlobs(self,blob,trees):
        if blob not in trees:
            trees.append(blob)
            if blob.isDir():
                for b in blob.files.values():
                    self.__listBlobs(b,trees)

    def dump(self):
        trees=[]
        self.__listBlobs(self.root,trees)
        return StorjFSEncoder().encode(trees)



class StorjFSEncoder(json.JSONEncoder):
    def default(self,o):
        if isinstance(o,Blob) or isinstance(o,Tree):
            return o.getDict()
        return json.JSONEncoder.default(self, o)




if __name__ == '__main__':
    fs=StorjFS()
    fs.createFile("/test.txt",b'test data')
    fs.createDir("/moe")
    fs.createFile("/moe/test2.txt",b'test2 data')
    print(fs.readFile("/test.txt"))
    print(fs.readFile("/moe/test2.txt"))
    print("ls /")
    root=fs.readDir("/")
    for f in root.keys():
        print(f)
    root=fs.readDir("/moe")
    print("ls /moe")
    for f in root.keys():
        print(f)
    fs.unlink("/moe/test2.txt")
    j=fs.dump()
    print(j)
    fs.load(j)
    print("ls /moe")
    root=fs.readDir("/moe")
    for f in root.keys():
        print(f)
