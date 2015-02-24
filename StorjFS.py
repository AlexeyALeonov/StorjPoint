# coding: utf-8

import time
import logging
import json
import io
import bz2

from BlobTree import Blob 
from BlobTree import Tree 
import storj

class StorjFS:
    def __init__(self,hash=-1,key=-1):
        if hash==-1 or key==-1:
            self.root=Tree(0o755)
        else:
            data=bz2.decompress(storj.download(hash,key))
            self.load(data)

    def load(self,jtext):
        blobs=[]
        trees=[]

        objs=json.loads(jtext)
        for obj in objs:
            print("!!!")
            print(obj)
            if obj['type']=='tree':
                tree=Tree.fromJson(obj)
                trees.append(tree)
                blobs.insert(obj['no'],tree)
            if obj['type']=='blob':
                blob=Blob.fromJson(obj)
                blobs.insert(obj['no'],blob)

        for t in trees:
            for k,v in t.files.items():
                print(k)
                print(v)
                print(blobs[v])
                t.files[k]=blobs[v]
        self.root=blobs[0]
 
    def __downloadByBlob(self,blob):
        if blob.isDir():
            raise Exception('permission denied')
        if not blob.isReadable():
            raise Exception('permission denied')
        return storj.download(blob.hash,blob.passwords)

    def save(self,inode,dirInfo):
        data=bz2.compress(self.dump())
        return storj.upload("storjfs.dat",data)

    def __searchParentTree(self,path):
        dirs=path.split('/')
        while '' in dirs:
            dirs.remove('')

        tree=self.root
        name=None
        if len(dirs)>0:
            name=dirs[len(dirs)-1]
            for p in dirs[0:-1]:
                if p not in tree.files:
                      return (None,None)
                tree=tree.files[p]
        return (tree,name)

    def __getFilename(self,path):
        dirs=path.split('/')
        return dirs[len(dirs)-1]

    def __deleteFromStorj(self,blob):
        if blob.counter==0 and not blob.isDir():
            storj.delete(blob.hash)
        
    def getBlob(self,path):
        (parent,name)=self.__searchParentTree(path)
        if parent==None and name==None:
            raise FileNotFoundError()
        if name==None:
            blob=parent
        else:
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
        toDir.addFile(name,fromBlob)

    def setPermission(self,path,permission):
        self.getBlob(path).setPermission(permission)

    def updateFile(self,path,data,permission=0o755):
        (parent,name)=self.__searchParentTree(path)
        pre=self.getBlob(path)
        if pre!=None:
            permission=pre.permission
            self.__deleteFromStorj(pre)
            parent.unlink(name)
        (hash,key)=storj.upload(name,data)
        blob=Blob(hash,len(data),permission,key)
        parent.addFile(name,blob)

 
    def createDir(self,path,permission=0o755):
        (parent,name)=self.__searchParentTree(path)
        tree=Tree(permission,parent)
        parent.addFile(name,tree)

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
        blob=parent.unlink(name)
        self.__deleteFromStorj(blob)


    def move(self,fromm,dest,overwrite=True):
        (destParent,destName)=self.__searchParentTree(dest)
        if destParent.files[destName]!=None:
            if not overwite:
                raise FileExistsError()
            blob=destParent.unlink(destName)
            self.__deleteFromStorj(blob)
        (fromParent,fromName)=self.__searchParentTree(fromm)
        destParent.addFile(fromParent.files[fromName])
        fromParent.unlink(fromName)

    def __listBlobs(self,blob,trees):
        if blob not in trees:
            trees.append(blob)
            if blob.isDir():
                for b in blob.files.values():
                    self.__listBlobs(b,trees)

    def dump(self):
        trees=[]
        self.__listBlobs(fs.root,trees)
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
