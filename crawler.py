#coding=utf-8

import sys,os
import re
import socket
import time
from urllib import urlopen,urlretrieve
import urllib2
import hashlib

class Crawler:
    def open_read(self,url,proxy='0'):
        if proxy=="0":
            socket.setdefaulttimeout(20) #try except @line 30: read()
            try:
                page = urlopen(url)
                print "connecting "+url
                content = page.read()
                print "open link success"
                page.close()
                return content
            except IOError:
                print "timeout, link="+url
        else:
            try:
                proxy_support = urllib2.ProxyHandler({'http':proxy})
                opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
                urllib2.install_opener(opener)
                return urllib2.urlopen(url).read()
            except:
                print "proxy error"

    def initSets(self,done_set_file):
        self.wm_domain='http://www.bdwm.net/bbs/'
        self.data_dir = 'F:\\IS10\\grad\\data\\'
        f = open(self.data_dir+done_set_file,'r')
        self.url_set = set()
        self.url_swap_set = set()
        self.done_set= set()
        for i in f.read():
            self.done_set.add(i)
        f.close
    def saveDoneSet(self,done_set_file):
        f = open(self.data_dir+done_set_file,'w')
        f.write(' '.join(self.done_set))
        f.close
    def doPage(self,url):
        '''
            save in-page text
            load in-page link
            update done_set
        '''
        hash_url = 'A'+hashlib.md5(url).hexdigest()
        f = open(self.data_dir+hash_url,'w')
        t = self.getHtmlText(self.open_read(url))
        f.write(t)
        f.close()
        #self.done_set.add(hash_url)
    def getHtmlText(self,html):
        r = re.compile(r'>(.*?)<').findall(html)
        return ' '.join(r)
    def getHtmlLinks(self,html):
        r = re.compile(r'href=.(.*?)\'').findall(html)
        for i in r:
            self.url_swap_set.add(str(i))
    def run(self,url):
        html = self.open_read(url)
        self.getHtmlLinks(html)
        self.url_set = self.url_set-self.done_set
        cnt = 0
        while cnt < 10:
            if len(self.url_set) < 2 and len(self.url_swap_set) < 2:
                return
            if len(self.url_set) < 2:
                self.url_set, self.url_swap_set=self.url_swap_set, self.url_set
            for i in self.url_set:
                url = self.wm_domain + i
                self.doPage(url)
                cnt = cnt + 1
            self.saveDoneSet('done.some')

class WmCrawler:

    crawler = Crawler()
    def openread(self,url):
        return self.crawler.open_read(url)
    def crawl_board(self,name_board,url='0'):
        if url == '0':
            html_board = self.openread('http://www.bdwm.net/bbs/bbsdoc.php?board='+str(name_board))
        else:
            html_board = self.openread(url)
        f = open('F:\\IS10\\grad\\data\\'+'A'+str(name_board),'a')
        url_wire = re.compile('bbscon.*?dig=\"').search(html_board).group(0)
        link_flag = 3
        t = time.time()
        cnt = 0
        mark = 0
        while link_flag == 3:
            try:
                html_wire = self.openread('http://www.bdwm.net/bbs/'+url_wire)
                text_wire = re.compile(r'>([^<]*)<').findall(html_wire)
                link_flag = len(re.compile(r'bbscon').findall(html_wire))
                f.writelines(' '.join(text_wire).replace('\n','\t'))
                url_wire = re.compile(r'bbscon.php[^\"]*').search(html_wire).group(0)
            except:
                link_flag = 2
            cnt = cnt + 1
        f.close()
        print time.time()-t
                
if __name__ == "__main__":
    #dbg = Crawler()
    #dbg.initSets('done.wm.web')
    dbg = WmCrawler()
    bd = 'sysop vote bbslists notepad Test Dance Board Science Linux IBMThinkPad LifeScience BBShelp Mechanics Emprise'.split(' ')
    for i in bd:
        dbg.crawl_board(i)
    

