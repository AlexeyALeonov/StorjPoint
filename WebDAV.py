from flask import Flask,request,make_response
from lxml import etree

app = Flask(__name__)

@app.route('/', defaults={'path': ''},methods=['OPTIONS'])
@app.route('/<path:path>',methods=['OPTIONS'])
def options(path):
    response = make_response()
    response.headers['Allow'] = 'GET, POST, DELETE, PROPPATCH, MOVE, MKCOL, COPY, PROPFIND'
    response.headers['DAV']='1'
    return response

@app.route('/', defaults={'path': ''},methods=['PROPFIND'])
@app.route('/<path:path>',methods=['PROPFIND'])
def propfind(path):
    depth=request.headers.get('Depth')
    host="http://"+request.headers.get('Host')+path
    D='{DAV:}'
    M='{urn:schemas-microsoft.com:}'


    multistatus = etree.Element(D+'multistatus', nsmap={'D': 'DAV:','M': 'urn:schemas-microsoft.com:'}  )            

    response = etree.SubElement(multistatus, D+'response')      
    etree.SubElement(response, D+'href').text=host
    propstat = etree.SubElement(response, D+'propstat')      
    prop = etree.SubElement(propstat, D+'prop')      
    resourcetype = etree.SubElement(prop, D+'resourcetype')      
    etree.SubElement(resourcetype, D+'collection')      
    etree.SubElement(prop, M+'Win32FileAttributes').text='00000011'
    etree.SubElement(propstat, D+'status').text='HTTP/1.1 200 OK'
    if depth=='0':
        print( etree.tostring(multistatus, encoding="utf-8",xml_declaration=True))
        return  etree.tostring(multistatus, encoding="utf-8",xml_declaration=True),207

    if depth=='1':
        response = etree.SubElement(multistatus, D+'response')      
        etree.SubElement(response, D+'href').text=host+'/'+'a.txt'
        propstat = etree.SubElement(response, D+'propstat')      
        prop = etree.SubElement(propstat, D+'prop')      
        etree.SubElement(prop, D+'getcontentlength').text='123'
        etree.SubElement(prop, D+'getcontenttype').text='application/octet-stream'
        etree.SubElement(prop, M+'Win32CreationTime').text='Sat, 21 Feb 2015 13:03:01 GMT'
        etree.SubElement(prop, M+'Win32LastAccessTime').text='Sat, 21 Feb 2015 13:03:01 GMT'
        etree.SubElement(prop, M+'Win32LastModifiedTime').text='Sat, 21 Feb 2015 13:03:01 GMT'
        etree.SubElement(prop, M+'Win32FileAttributes').text='00000000'
        etree.SubElement(propstat, D+'status').text='HTTP/1.1 200 OK'
        print( etree.tostring(multistatus, encoding="utf-8",xml_declaration=True))
        return  etree.tostring(multistatus, encoding="utf-8",xml_declaration=True),207

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=80,debug=True)

