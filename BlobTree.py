import pickle
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

class Blob:
    def __init__(self,hash,size,permission,passwd):
        self.hash=hash
        self.size=size
        self.user=0
        self.group=0
        self.permission=S_IFREG | permission
        self.ctime=time.ctime()
        self.mtime=time.ctime()
        self.atime=time.ctime()
        self.counter=0
        self.passwords=passwd

    def unlink(self):
        self.counter=self.counter-1
        return self.counter==0

    def updateMtime(self):
        self.mtime=time.ctime()

    def updateAtime(self):
        self.atime=time.ctime()

    def getPermission(self):
        return self.permission & o777

    def setPermission(self,permisson):
        permisson=self.permission & I_IFREG

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

class Tree(Blob):
    def __init__(self,permission,parent=''):
        if parent=='':
            parent=self
        Blob.__init__(self,0,0,permission,[])
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
        permisson=self.permission & I_IFDIR
