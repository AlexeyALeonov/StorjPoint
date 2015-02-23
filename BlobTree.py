# coding: utf-8

import pickle
import time
import logging
import binascii

S_IFDIR=0o40000
S_IFREG=0o100000
S_IFLNK=0o120000

S_IRUSR=0o400	
S_IWUSR=0o200
S_IXUSR=0o100

S_IRGRP=0o40
S_IWGRP=0o20
S_IXGRP=0o10

S_IROTH=0o4
S_IWOTH=0o2
S_IXOTH=0o1

class Inode:
    inodeNo=0
    def __init__(self,permission):
        self.user=0
        self.group=0
        self.permission=permission
        self.ctime=int(time.time())
        self.mtime=int(time.time())
        self.atime=int(time.time())
        self.counter=0
        self.no=Inode.inodeNo
        Inode.inodeNo= Inode.inodeNo+1

    def updateMtime(self):
        self.mtime=int(time.time())

    def updateAtime(self):
        self.atime=int(time.time())

    def getPermission(self):
        return self.permission & o777

    def isDir(self):
        return self.permission & S_IFDIR !=0

#TBD
    def isReadable(self):
        return self.permission & S_IRUSR !=0

#TBD
    def isWritable(self):
        return self.permission & S_IWUSR !=0

#TBD
    def isExecutable(self):
        return self.permission & S_IXUSR !=0

    def getDict(self):
        return {'user':self.user,'group':self.group,'permission':self.permission,
                'ctime':self.ctime,'mtime':self.mtime,'atime':self.atime,
                'counter':self.counter,'no':self.no}

class Blob(Inode):
    def __init__(self,hash,size,permission,passwd):
        super(Blob,self).__init__(permission|S_IFREG)
        self.hash=hash
        self.size=size
        self.passwords=passwd

    def setPermission(self,permisson):
        permisson=self.permission | I_IFREG

    def getDict(self):
        hash=str(binascii.hexlify(self.hash),'ascii')
        key=str(binascii.hexlify(self.passwords[0]),'ascii')
        result=super(Blob,self).getDict()
        result.update({'type':'blob','hash':hash,'passwords':[key],'size':self.size})
        return result

    @staticmethod
    def fromJson(obj):
        hash=binascii.unhexlify(obj['hash'])
        passwords=[]
        for h in obj['passwords']:
            passwords.append(binascii.unhexlify(h))
        blob=Blob(hash,obj['size'],obj['permission'],passwords)
        blob.no=obj['no']
        return blob


class Tree(Inode):
    def __init__(self,permission,parent=''):
        if parent=='':
            parent=self
        super(Tree,self).__init__(permission|S_IFDIR)
        self.permission=S_IFDIR | permission
        self.files={".":self,"..":parent}

    def addFile(self,name,blob):
        if self.isWritable()==False:
            raise Exception('permission denied')
        blob.counter=blob.counter+1
        if name in self.files:
            blob.ctime=self.files[name].ctime
        self.files[name]=blob

    def unlink(self,name):
        if self.isWritable()==False:
            raise Exception('permission denied')
        blob=self.files[name]
        if blob==None:
            raise Exception('file not found')
        if blob.isWritable()==False:
            raise Exception('permission denied')
        blob.counter=blob.counter-1
        del(self.files[name])
        return blob

    def setPermission(self,permisson):
        permisson=self.permission | S_IFDIR

    def getDict(self):
        fs={}
        for k,v in self.files.items():
            fs[k]=v.no
        result=super(Tree,self).getDict();
        result.update({'type':'tree','files':fs})
        return result

    @staticmethod
    def fromJson(obj):
        tree=Tree(obj['permission'])
        tree.no=obj['no']
        for k,v in obj['files'].items():
            tree.files[k]=v
        return tree
