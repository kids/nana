#encoding=utf-8

"""
by Roi @IS10.PKU

It is a script used to crawl sina Weibo contents,
which are used as raw data for the purpose of my graduation thesis only.

IE is called in the script through python win32com module, so as to get
XMLHttpRequest data in Weibo pages. Therefore it could be further applied
to Twitter, Facebook, Renren etc., with the intent of reasch restrictly.

To run the crawler, class IdCollector is to crawl target user ids,
while the other is the content crawler scanning target id list.

Jan 2013
"""

from win32com.client import DispatchEx
import re
import time

'''
This implementation use default session of the ie browser,
such as cookies

Also, the brower is able to run backgroudly, set visibility
in __init__ method

On the contrary refer the other, selenium one
'''

def bkup_cookie_zhihu():
	import hashlib
	import pickle
	from bs4 import BeautifulSoup
	from selenium import webdriver

	oper = Opener()
	u_set0=set()
	u_set1=set()
	b=webdriver.Firefox()
	b.get('http://zhihu.com')
	cookies=pickle.load(open('/Users/r/Downloads/zhihu.pickle','r'))
	for cookie in cookies:
	    b.add_cookie(cookie)

class IdCollector:
    def __init__(self,url='about:blank'):
        self.ie = DispatchEx('InternetExplorer.Application')
        self.ie.Visible = 0
        time.sleep(0.5)

    def openFullPage(self,url):
        '''
            for the purpose html file is complete
            this one is for pages without XHR
            print page title and page url for debugging
        '''
        self.ie.Navigate(url)
        while self.ie.Busy:
            time.sleep(0.1)
        print self.ie.LocationName, self.ie.LocationURL

    def initSets(self)	:
        '''
            init 3 sets for swap saving user id for the class instance,
            1 for current seeds
            1 for saving current result, 1 crawled seeds
        '''
        self.collected_set, self.collector_set, self.doing_set = \
                            self.loadIdFilesToSets('collected.ids','collector.ids','doing.ids')
        self.set_size = len(self.collected_set)+len(self.collector_set)+len(self.doing_set)
        print 'there are totally',str(self.set_size),'entries in sets'
        
    def backupMem(self):
        '''backup THE3 sets from memory to file'''
        if len(self.collected_set)+len(self.collector_set)+len(self.doing_set)-self.set_size>1000:
            self.writeToIdFiles('collected.ids','collector.ids','doing.ids')
            self.set_size = len(self.collected_set)+len(self.collector_set)+len(self.doing_set)

    def getIdsOnePage(self,html):
        '''return a set of all ids in given html'''
        uids = re.compile(r'uid=(\d+)').findall(html)
        page_id_set = set()
        for uid in uids:
            page_id_set.add(int(uid.encode('ascii')))
        return page_id_set

    def getIdFollowUrl(self,uid,page):
        '''return url of follower page given uid and page'''
        return ''.join(['http://weibo.com/',str(uid),'/follow?page=',str(page)])

    def combineSet(self,current_set):
        new_id_set = current_set - self.collected_set - self.doing_set
        self.collector_set = self.collector_set.union(new_id_set)

    def currentHtml(self):
        return self.ie.Document.body.outerHTML
    
    def getIdPage(self,uid,page=1):
        '''
            get ids from a given uid, by update collector set,
            default is 'Breadth-First', getting 1st page of follower
        '''
        url = self.getIdFollowUrl(uid,page)
        self.ie.Navigate(url)
        html = self.currentHtml()
        this_set = self.getIdsOnePage(html)
        self.combineSet(this_set)
        print len(self.collector_set),len(self.collected_set),len(self.doing_set)
        '''
            To crawl ids in 'Deep First' way, using following codes
        if html.find('page='+str(page+1))>1:
            page = page+1
            self.getIdPage(uid,page)
        '''
        
    def loadIdFilesToSets(self,fcollected,fcollector,fdoing,d='F:\\IS10\\grad\\data\\'):
        '''init THE3 sets from file'''
        [fcollected,fcollector,fdoing]=[''.join([d,str(f)]) for f in (fcollected,fcollector,fdoing)]
        f1,f2,f3 = open(fcollected,'r'),open(fcollector,'r'),open(fdoing,'r')
        fh = (f1,f2,f3)
        scollected,scollector,sdoing = set(),set(),set()
        sh = (scollected,scollector,sdoing)
        print 'Time before load to set:',str(time.ctime())
        for i in range(3):
            for ele in fh[i].read().split(' '):
                sh[i].add(ele)
            fh[i].close
        print 'Time after loaded to set:',str(time.ctime())
        return (scollected,scollector,sdoing)

    def writeToIdFiles(self,fcollected,fcollector,fdoing,d='F:\\IS10\\grad\\data\\'):
        '''save id sets to file'''
        [fcollected,fcollector,fdoing]=[d+f for f in (fcollected,fcollector,fdoing)]
        f1,f2,f3 = open(fcollected,'w'),open(fcollector,'w'),open(fdoing,'w')
        fh = (f1,f2,f3)
        sh = (self.collected_set, self.collector_set, self.doing_set)
        for i in range(3):
            print 'T0 saving set to file:',str(time.ctime())
            fh[i].write(' '.join([str(ele) for ele in sh[i]]))
            print 'T1 saving set to file:',str(time.ctime())
            fh[i].close()

class Wcontent:
    def __init__(self):
        self.ie = DispatchEx('InternetExplorer.Application')
        self.ie.Visible = 1
        time.sleep(0.5)
        
    def openFullPage(self,url):
        self.ie.Navigate(url)
        while self.ie.Busy:
            time.sleep(0.5)
        print self.ie.LocationName, self.ie.LocationURL

    def openXHRFull(self,url):
        '''
            get complete page for html
            for XHR content page
        '''
        self.ie.Navigate(url)
        while self.ie.Busy:
            time.sleep(0.1)
        print self.ie.LocationName, self.ie.LocationURL
        t0 = time.time()
        while self.currentHtml().find('page=')==-1:
            self.ie.Document.parentWindow.execScript('window.scrollTo(0,document.body.scrollHeight-500)')
            time.sleep(0.1)
            if time.time() - t0 > 5:
                self.ie.refresh()

    def initSet(self):
        '''init target/done id set from file'''
        self.preUrl = 'http://weibo.com/u/'
        self.data_dir = 'F:\\IS10\\grad\\data\\'
        self.uid_set = set()
        self.done_content_set = set()
        self.loadIdFilesToSet(['collected.ids'],'done.content.ids')

    def backupDoneSet(self):
        '''save done id set to file'''
        print 'saving done set to file'
        self.bf = open(self.data_dir+'done.content.ids','a')
        self.bf.write(' '+' '.join(str(ele) for ele in self.done_content_set))
        self.bf.close()
        
    def currentHtml(self):
        return self.ie.Document.body.outerHTML
            
    def	getPageText(self,url):
        '''
            return plain Weibo text from given url
            using div=WB_text to filter
        '''
        self.openXHRFull(url)
        html = self.currentHtml()
        txt = re.compile(r'WB_text(.*?)div').findall(html)
        if txt:
            for i,line in enumerate(txt):
                txt[i] = ''.join(re.compile(r'>(.*?)<').findall(line)).split('//')[0]
            return '\n'.join(txt)
        else:
            return ''
            
    def getIdContentUrl(self,uid,page=1):
        return ''.join([self.preUrl,str(uid),'?page=',str(page)])

    def pageCnts(self,html):
        '''return Weibo owner nick name and counts'''
        fname = re.compile(r'fname=(.*?)&').search(html)
        if fname != None:
            wb_cnt = re.compile(r'tagweibo[^>]*>[^>]*>(\d+)<').search(html).group(1)
            fans_cnt = re.compile(r'tagfans[^>]*>[^>]*>(\d+)<').search(html).group(1)
            follow_cnt = re.compile(r'tagfollow[^>]*>[^>]*>(\d+)<').search(html).group(1)
            return fname.group(1),follow_cnt,fans_cnt,wb_cnt
        '''
            To e.weibo & media.weibo page cnts
        fname = re.compile(r'title_big..[\n](.*?)[\n]').search(html)
        if fname != None:
            cseg = re.compile(r'strong>(\d+)<').findall(html)
            self.preUrl = 'http://e.weibo.com/'
            return '#e#'+fname.group(1),cseg[0],cseg[2],cseg[4]
        '''
        #retry
        return '##',0,0,0
    
    def getIdContent(self,uid):
        '''
            Main portal to content crawling over uid
            allow controlling by wb_cnt of given uid
        '''
        url = self.getIdContentUrl(uid)
        self.openFullPage(url)
        if self.ie.LocationURL.find('media.weibo')==7 or self.ie.LocationURL.find('e.weibo')==7:
            return (self.ie.LocationName,0,0,0),''
        
        html = self.currentHtml()
        #id_cnts = (fname,follow_cnt,fans_cnt,wb_cnt)
        id_cnts = self.pageCnts(html)
        print id_cnts
        wb_cnt = id_cnts[3]
        if int(wb_cnt) < 45:
            return (id_cnts,'')
        if int(wb_cnt) > 900:
            #self.getIdOriContent(uid,id_cnts)
            wb_cnt = 2000
        content = ''
        for page in range(1,int(wb_cnt)/45+2):
            url = self.getIdContentUrl(uid,page)
            #page_content = self.browser.get_text('class=WB_feed')
            page_content = self.getPageText(url)
            content = content + page_content
        return (id_cnts,content)
                
    def getIdOriContentUrl(self,uid,page=1):
        return ''.join([self.preUrl,str(uid),'?ori=1','&page=',str(page)])

    def getIdOriContent(self,uid,id_cnts):
        '''
            When the user is too noisy
            crawler her original content pages
        '''
        url = self.getIdOriContentUrl(uid)
        self.openXHRFull(url)
        time.sleep(1)
        html = self.currentHtml()
        page = self.getMaxPage(html)
        print page
        content = self.getPageText(url)
        for page in range(2,int(page)+1):
            url = self.getIdOriContentUrl(uid,page)
            page_content = self.getPageText(url)
            content = content + page_content
        return (id_cnts,content)
        
    def getMaxPage(self,html):
        maxi = re.compile(r'page=(/d+)').search(html)
        if maxi:
            page = maxi.group(0)
        else:
            page = 1
        return page
			
    def loadIdFilesToSet(self,uid_files,done_file):
        uid_file_paths = [self.data_dir+f for f in uid_files]
        done_file_hdl = open(d+done_file,'r')
        print 'Time before load to set:',str(time.ctime())
        for file_path in uid_file_paths:
            file_handle = open(file_path,'r')
            t_set = set()
            for ele in file_handle.read().split(' '):
                t_set.add(ele)
            self.uid_set = self.uid_set.union(t_set)
            file_handle.close()
        for ele in done_file_hdl.read().split(' '):
            self.done_content_set.add(ele)
        done_file_hdl.close()
        print 'Time after loaded to set:',str(time.ctime())
        print len(self.uid_set)

    def writeIdContent(self,uid'):
        fh = open(self.data_dir+str(uid),'w')
        cnt,text = self.getIdContent(uid)
        fh.writelines(cnt[0].encode('utf-8')+' '+' '.join(str(c) for c in cnt[1:]))
        fh.write(text.encode('utf-8'))
        fh.close()
        self.done_content_set.add(uid)#''.join([str(uid),'||',cnt[0].encode('utf-8')]))

		
def runIdCraw(url='http://weibo.com/10pku'):
    '''
        This is the id crawler runner,
        it could not be a class for win32com can not be instance
    '''
    rpm = RoiPamie()
    rpm.initSets()
    if len(rpm.doing_set)<2 and len(rpm.collector_set)<2:
        rpm.openFullPage(url)
        html = rpm.currentHtml()
        rpm.doing_set = rpm.getIdsOnePage(html)
    print 'sdoing',str(len(rpm.doing_set))
    
    while len(rpm.collected_set)+len(rpm.collector_set)+len(rpm.doing_set)<10000:
        if len(rpm.doing_set)<=1 and len(rpm.collector_set)>1:
            rpm.collector_set,rpm.doing_set = rpm.doing_set,rpm.collector_set
        for i in rpm.doing_set:
            rpm.collected_set.add(i)
            rpm.getIdPage(i) #weak diversity if crawling all pages
            rpm.backupMem()
        rpm.doing_set = set()
    rpm.backupMem()


def runCtnCraw():
    '''
        This is the Weibo content crawler runner
        exceptions including page opening error
    '''
    dbg = Wcontent()
    id_size = 0
    t=time.time()
    dbg.initSet()
    working_set=dbg.uid_set-dbg.done_content_set
    for uid in working_set:
        try:
            dbg.writeIdContent(uid)
        except:
            continue
        if id_size%10 == 0:
            dbg.backupDoneSet()
            print time.time()-t
        id_size = id_size + 1
    dbg.backupDoneSet()


	
if __name__=='__main__':
    #runIdCraw()
    runCtnCraw()
    #dbg=Wcontent()
   

    
