# coding: utf-8

import time
import logging

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

#TBD
    def setReadable(self,setbit):
        if setbit:
          self.permission= self.permission | S_IRUSR
        else:
          self.permission= self.permission & ~(S_IRUSR)

#TBD
    def setWritable(self,setbit):
        if setbit:
          self.permission= self.permission | S_IWUSR
        else:
          self.permission= self.permission & ~(S_IWUSR)

#TBD
    def setExecutable(self,setbit):
        if setbit:
          self.permission= self.permission | S_IXUSR
        else:
          self.permission= self.permission & ~(S_IXUSR)


    def getDict(self):
        return {'user':self.user,'group':self.group,'permission':self.permission,
                'ctime':self.ctime,'mtime':self.mtime,'atime':self.atime,
                'counter':self.counter,'no':self.no}

    def fromJson(self,obj):
        self.user=obj['user']
        self.group=obj['group']
        self.ctime=obj['ctime']
        self.mtime=obj['mtime']
        self.atime=obj['atime']
        self.counter=obj['counter']
        self.no=obj['no']


class Blob(Inode):
    def __init__(self,hash,size,permission,passwd):
        super(Blob,self).__init__(permission|S_IFREG)
        self.hash=hash
        self.size=size
        self.passwords=passwd

    def setPermission(self,permisson):
        permisson=self.permission | I_IFREG

    def getDict(self):
        result=super(Blob,self).getDict()
        result.update({'type':'blob','hash':self.hash,
            'passwords':self.passwords,'size':self.size})
        return result

    @staticmethod
    def fromJson(obj):
        blob=Blob(obj['hash'],obj['size'],obj['permission'],obj['passwords'])
        super(Blob,blob).fromJson(obj)
        return blob

class Tree(Inode):
    def __init__(self,permission,parent=''):
        if parent=='':
            parent=self
        super(Tree,self).__init__(permission|S_IFDIR)
        self.permission=S_IFDIR | permission
        self.files={".":self,"..":parent}

    def addFile(self,name,blob):
        if not self.isWritable():
            raise PermissionError()
        blob.counter=blob.counter+1
        self.files[name]=blob

    def unlink(self,name):
        if not self.isWritable():
            raise PermissionError()
        blob=self.files[name]
        if blob==None:
            raise FileNotFoundError()
        if not blob.isWritable():
            raise PermissionError()
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
        super(Tree,tree).fromJson(obj)
        return tree
