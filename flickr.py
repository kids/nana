#Key:5a080fff14bf939fee624ef736ae86d4
#Secret:6b24ba381f93afa4


import sys,os
import re
import socket
from urllib import urlopen,urlretrieve
import urllib2

def processpage(url,proxy):
    if proxy=="0":
        socket.setdefaulttimeout(20) #try except @line 30: read()
        try:
            page = urlopen(url)
            print ("connecting",url)
            content = page.read()
            print "open link success"
            page.close()
            return content
        except IOError:
            print ("timeout, link=",url)
    else:
        try:
            proxy_support = urllib2.ProxyHandler({'http':proxy})
            opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
            urllib2.install_opener(opener)
            return urllib2.urlopen(url).read()
        except:
            print "proxy error"


def urldown(month,day):
    #http://www.flickr.com/explore/interesting/2012/09/02/
    #<a data-track="thumb" href="/photos/steinamatt/7917304342/" title="Holtsbryggja by SteinaMatt">
    #http://www.flickr.com/photos/mark_lj/7915346450/sizes/h/in/photostream/ large
    #http://www.flickr.com/photos/michaeljclausen/7913691562/sizes/o/in/photostream/ original
    dayportal = 'http://www.flickr.com/explore/interesting/2012/%02d/%02d/' %(month,day)
    daypage = processpage(dayportal,'0')
    go = re.compile('data.track..thumb..href..([^\"]*)')
    dailyl = re.findall(go,daypage)
    for thumb in dailyl:
        imgweb = 'http://www.flickr.com'+thumb+'sizes/h/in/photostream/'
        imgpage = processpage(imgweb,'0')
        gs = re.compile('http.*?d.jpg')
        try:
            imgurl = re.search(gs,imgpage).group()
            ImgWrite(imgurl)
        except:
            continue


def ImgRetrive(imgurl):
    imgname = imgurl.split('/')[-1]
    imgpath = imgdir+imgname    
    try:
        if os.path.exists(imgpath):
            print imgpath+" exist"
        else:
            urlretrieve(imgurl, imgpath)
            print imgname+" saving to: "+imgpath 
    except:
        print "Picture("+imgname+") failed"

    
def ImgWrite(imgurl):
    imgname = imgurl.split('/')[-1]
    imgpath = imgdir+imgname    
    try:
        if os.path.exists(imgpath):
            print imgpath+" exist"
        else:
            img = processpage(imgurl,'127.0.0.1:8000')
            f = open(imgpath,'wb')
            f.write(img)
            print imgname+" saving to: "+imgpath 
    except:
        print "Picture("+imgname+") failed"

            
if __name__ == "__main__":
    imgdir = "D:\\i\\"
    for mth in range(1,9):
        for dy in range(1,28):
            urldown(mth,dy)
