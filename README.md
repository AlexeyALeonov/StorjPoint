![](https://raw.githubusercontent.com/storj-jp/StorjPoint/master/icon.png) 
#StorjPoint -  File System for Storj.

StorjPoint is a file system for Storj.
SotjPoint also supply WebDAV server, which enables you to handle files in Storj in windows explorer.

## Promotion Video
http://youtu.be/IztV_eEGE2Y

## Requirements
StorjPoint requires Python 3.x, also uses flask,lxml, and require python modules.

## Installation

    $ virtualenv env
    $ source env/bin/activate
    $ python setup.py install
    $ suo python StorjPoint.py
    

## Usage

    $sudo python StorjPoint/StorjPoint.py

Now StorjPoint is running on port 80.
(Windows Explore in XP only works with WebDAV server on port 80.)


## Layers of StorjPoint
windows explorer -> WebDAV server -> StorjFS -> Storj API(MetaDisk API) ->Storj network

### Storj API
At the bottom of the layer , StorjPoint uses [MeataDisk API](http://github.com/storj/web-core).
For now StorjPoint uses only 3 APIs that gets token, uploads/downloads files.

### StorjFS layer
[Storj](http://storj.io) stores files, but doesn't supply directories, which means it doesn't supply file system. You can upload to/download from files , but you cannot create directories.

StorjPoint supplies 'Storj File System(StorjFS)' as Python class. You can handle files as in *nix-like file system, such as create/write/read/delete files and directories.

Files in Storj are handled like blobs in [git](http://git-scm.com/).  But whole of directories(trees in git)are stored in one python dict(hash) and are stored in one file in Storj for efficiency. it is not like git where each of trees(directories) are stored as one file. In the future when many directies will be created, more efficiency would be needed.

StorjFS also supplies cache. Once files in StorjFS created, data would be stored in local directory as chunks for caching. After caching, file in StorjFS needs to be read, data in cache is used. Data chunks woudl be updloaded in backgound peridically.

When files in Storjfs need to be read but not cached, StorjFS would donwload data from StojFS and write cache data, and cache would be read as data. data would be read and be written to cache simultaneously.

### WebDAV Server
StorjFS implements WebDAV server by Flask on top of StorjFS.
Windows Explorer can read WebDAV server as like a smb server, i.e. you can 'explorer' files/directories in WebDAV server as in a normal disk.
StorjPoint implements minimum WebDAV functions for windows explorer in XP,Vista. I didn't check 7,8, and other WebDAV clients. 

##Contribution

Improvements to the codebase and pull requests are encouraged.


