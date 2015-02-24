# coding: utf-8

from lxml import etree
import time

ReadOnly = 0x00000001
Hidden = 0x00000002
System = 0x00000004
Directory = 0x00000010
Normal = 0x00000080
Temporary = 0x00000100
Compressed = 0x00000800
Encrypted = 0x00004000
NoBuffering = 0x20000000
PosixSemantics = 0x01000000

D='{DAV:}'
M='{urn:schemas-microsoft.com:}'

class DAVXml:
    def __init__(self,host,root,fs):
        self.host=host
        self.root=root
        self.fs=fs

    def __propstatRoot(self,multistatus):
        response = etree.SubElement(multistatus, D+'response')      
        etree.SubElement(response, D+'href').text=\
            'http://'+self.host+'/'+self.root
        propstat = etree.SubElement(response, D+'propstat')      
        prop = etree.SubElement(propstat, D+'prop')      
        resourcetype = etree.SubElement(prop, D+'resourcetype')      
        etree.SubElement(resourcetype, D+'collection')      
        etree.SubElement(prop, M+'Win32FileAttributes').text=\
            '%08x' % (Directory |ReadOnly)
        etree.SubElement(propstat, D+'status').text='HTTP/1.1 200 OK'

    def __gmtime(self,sec):
        return strftime('%a, %d %b %Y %H:%M:%S GMT', sec)

    def __etime(self,sec):
        return int(time.mktime(time.strptime(p.text,'%a, %d %b %Y %H:%M:%S GMT')))


    def __attribute(self,blob):
        permission=0
        if not blob.isWritable():
            permission = permission & ReadOnly
        if blob.isDir():
            permission = permission & Directory
        return '%08x' % permission


    def propfind(self,path,depth):
        multistatus = etree.Element(D+'multistatus',nsmap=\
            {'D': 'DAV:','M': 'urn:schemas-microsoft.com:'})
        print(path+" "+self.host+" "+self.root)
        if path==self.root: 
            self.__propstatRoot(multistatus)
        else:
            if path.startswith(path):
                path.replace(self.root,'')
                blob=self.fs.getBlob(path)
                self.__propfindFile(blob,multstatus)
        if depth==1:
          for b in blob.files.keys():
              self.__propstatFile(b,multistatus)
        print( etree.tostring(multistatus, encoding="utf-8",xml_declaration=True))
        return  etree.tostring(multistatus, encoding="utf-8",xml_declaration=True)

    def __propfindFile(self,blob,multistatus):
            response = etree.SubElement(multistatus, D+'response')      
            if blob.isDir():
                resourcetype = etree.SubElement(prop, D+'resourcetype')      
                etree.SubElement(resourcetype, D+'collection')      
            etree.SubElement(response, D+'href').text=path
            propstat = etree.SubElement(response, D+'propstat')      
            prop = etree.SubElement(propstat, D+'prop')      
            if blob.isDir():
                etree.SubElement(prop, D+'getcontentlength').text='0'
            else:
                etree.SubElement(prop, D+'getcontentlength').text=blob.size
            etree.SubElement(prop, D+'getcontenttype').text=\
                'application/octet-stream'
            etree.SubElement(prop, M+'Win32CreationTime').text=\
                self.__gmtime(blob.ctime)
            etree.SubElement(prop, M+'Win32LastAccessTime').text=\
                self.__gmtime(blob.atime)
            etree.SubElement(prop, M+'Win32LastModifiedTime').text=\
                self.__gmtime(blob.mtime)
            etree.SubElement(prop, M+'Win32FileAttributes').text=\
                self.attribute(blob)
            etree.SubElement(propstat, D+'status').text='HTTP/1.1 200 OK'

    def proppatch(self,path,xml):
        root=etree.fromstring(xml)
        path.replace(self.root,'')
        blob=self.fs.getBlob(path)

        for p in root.find('.//'+D+'{DAV:}prop'):
            if p.tag==M+'Win32CreationTime':
                blob.ctime=self.__etime(p.text)
            if p.tag==M+'Win32LastAccessTime':
                blob.atime=self.__etime(p.text)
            if p.tag==M+'Win32LastModifiedTime':
                blob.mtime=self.__etime(p.text)
            if p.tag==M+'Win32FileAttributes':
                perm= BlobTree.S_IRUSR | BlobTree.S_IRGRP | BlobTree.S_IROTH
                if p.text & Directory !=0:
                    perm = perm | S_IFDIR
                else:
                    perm = perm | S_IFREG

                if p.text and Readonly==0:
                    perm=perm | BlobTree.S_IWUSR | BlobTree.S_IWGRP\
                              | BlobTree.S_IWOTH

        return self.propfind(path,0)

            
#xml=b'<?xml version="1.0" encoding="utf-8" ?><D:propertyupdate xmlns:D="DAV:" xmlns:Z="urn:schemas-microsoft-com:"><D:set><D:prop><Z:Win32CreationTime>Sat, 21 Feb 2015 13:03:47 GMT</Z:Win32CreationTime><Z:Win32LastAccessTime>Sat, 21 Feb 2015 13:03:47 GMT</Z:Win32LastAccessTime><Z:Win32LastModifiedTime>Sat, 21 Feb 2015 13:03:47 GMT</Z:Win32LastModifiedTime><Z:Win32FileAttributes>00000020</Z:Win32FileAttributes></D:prop></D:set></D:propertyupdate>'
