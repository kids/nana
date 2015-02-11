#encoding=utf-8
#java -jar selenium-server-standalone-2.x.x.jar

import re
import time
from selenium import selenium
#from selenium import webdriver
#from selenium.webdriver.common.keys import Keys

class RoiSelm:
    def __init__(self):
        self.uid_set = set()
        self.loadIdFilesToSet(['collected.ids'])
        self.browser = selenium('localhost',4444,'*chrome','http://google.com')
        self.browser.start()
        self.loginWeibo()

    def loginWeibo(self, name='if.vvvvw@yahoo.fr', pwd='zxcvbn'):
        '''login weibo'''
        loginurl='http://weibo.com/login.php'
        self.browser.open(loginurl)
        self.browser.wait_for_page_to_load(50)
        self.browser.type('loginname',name)
        self.browser.type('password',pwd)
        self.browser.click('class=W_btn_d')
        time.sleep(5)
        #self.browser.wait_for_page_to_load(5000)

    def openFull(self,url):
        self.browser.open(url)    
        self.browser.wait_for_page_to_load(500)
        for i in range(2):
            self.browser.run_script('window.scrollTo(0,document.body.scrollHeight-500)') #goto pageend
            self.browser.wait_for_page_to_load(500)
            
    def getIdContentUrl(self,uid,page=1):
        return ''.join(['http://www.weibo.com/u/',str(uid),'&page=',str(page)])

    def getIdContent(self,uid):
        url = self.getIdContentUrl(uid)
        self.openFull(url)
        html = self.browser.get_html_source()
        page = self.getMaxPage(html)
        if page > 20:
            self.getIdOriContent(uid,page)
        if page == 1:
            return (1,'')
        else:
            content = ''
            for page in range(int(page)):
                url = self.getIdContentUrl(uid,page)
                self.openFull(url)
                page_content = self.browser.get_text('class=WB_feed')
                content = content + page_content
            return (page,content)
                
    def getIdOriContentUrl(self,uid,page=1):
        return ''.join(['http://www.weibo.com/u/',str(uid),'?ori=1','&page=',str(page)])

    def getIdOriContent(self,uid,fpage):
        url = self.getIdOriContentUrl(uid)
        self.browser.open(url)
        html = self.browser.get_html_source()
        page = self.getMaxPage(html)
        content = ''
        for page in range(int(page)):
            url = self.getIdOriContentUrl(uid,page)
            self.openFull(url)
            page_content = self.browser.get_text('class=WB_feed')
            content = content + page_content
        return (fpage,content)
        
    def getMaxPage(self,html):
        maxi = re.compile(r'page=(/d+)').search(html)
        if maxi:
            page = maxi.group(0)
        else:
            page = 1
            
    def openIdContent(self,uid):
        #make sure logged in
        pass
        #selenium.get_text("//div[@id='1']/descendant::*[not(self::h1)]") #dom xpath
        #content = sel.get_text("td[@id='2']") #<td id="2">content I</td>
        
        #pt = sel.get_text('class=WB_feed')

    def loadIdFilesToSet(self,uid_files,d='F:\\IS10\\grad\\data\\'):
        uid_file_paths = [d+f for f in uid_files]
        print 'Time before load to set:',str(time.ctime())
        for file_path in uid_file_paths:
            file_handle = open(file_path,'r')
            t_set = set()
            for ele in file_handle.read().split(' '):
                t_set.add(ele)
            self.uid_set = self.uid_set.union(t_set)
        print 'Time after loaded to set:',str(time.ctime())
        print len(self.uid_set)

    def writeIdContent(uid,d='F:\\IS10\\grad\data\\'):
        fh = open(d+str(uid),'w')
        page,content = self.getIdContent(uid)
        fh.write(content)
        fh.close()
        self.done_content_set.add(''.join([str(uid),'||',str(page)]))
        #modify_after_each_crawl uids+nick

    
if __name__=='__main__':
    dbg = RoiSelm()
    s=dbg.getIdContent(2260303382)
    
