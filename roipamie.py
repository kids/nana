#encoding=utf-8

from win32com.client import DispatchEx
import re
import time

class RoiPamie:
    def __init__(self,url='about:blank'):
        self.ie = DispatchEx('InternetExplorer.Application')
        self.ie.Visible = 0
        time.sleep(0.5)

    def openFullPage(self,url):
        self.ie.Navigate(url)
        while self.ie.Busy:
            time.sleep(0.1)
        print self.ie.LocationName, self.ie.LocationURL
        #self.ie.Document.parentWindow.execScript('window.scrollTo(0,document.body.scrollHeight-500)')

    def initSets(self)	:
        self.collected_set, self.collector_set, self.doing_set = \
                            self.loadIdFilesToSets('collected.ids','collector.ids','doing.ids')
        self.set_size = len(self.collected_set)+len(self.collector_set)+len(self.doing_set)
        print 'there are totally',str(self.set_size),'entries in sets'
        
    def backupMem(self):
        if len(self.collected_set)+len(self.collector_set)+len(self.doing_set)-self.set_size>1000:
            self.writeToIdFiles('collected.ids','collector.ids','doing.ids')
            self.set_size = len(self.collected_set)+len(self.collector_set)+len(self.doing_set)

    def getIdsOnePage(self,html):
        uids = re.compile(r'uid=(\d+)').findall(html)
        page_id_set = set()
        for uid in uids:
            page_id_set.add(int(uid.encode('ascii')))
        return page_id_set

    def getIdFollowUrl(self,uid,page):
        return ''.join(['http://weibo.com/',str(uid),'/follow?page=',str(page)])

    def combineSet(self,current_set):
        new_id_set = current_set - self.collected_set - self.doing_set
        self.collector_set = self.collector_set.union(new_id_set)

    def currentHtml(self):
        return self.ie.Document.body.outerHTML
    
    def getIdPage(self,uid,page=1):
        url = self.getIdFollowUrl(uid,page)
        self.ie.Navigate(url)
        html = self.currentHtml()
        this_set = self.getIdsOnePage(html)
        self.combineSet(this_set)
        print len(self.collector_set),len(self.collected_set),len(self.doing_set)
        '''
        if html.find('page='+str(page+1))>1:
            page = page+1
            self.getIdPage(uid,page)
        '''
        
    def loadIdFilesToSets(self,fcollected,fcollector,fdoing,d='F:\\IS10\\grad\\data\\'):
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
        self.preUrl = 'http://weibo.com/u/'
        self.data_dir = 'F:\\IS10\\grad\\data\\'
        self.uid_set = set()
        self.done_content_set = set()
        self.loadIdFilesToSet(['collector.ids'],'done.content.ids')

    def backupDoneSet(self):
        print 't0 backup done set:',time.ctime()
        self.bf = open(self.data_dir+'done.content.ids','a')
        self.bf.write(' '+' '.join(str(ele) for ele in self.done_content_set))
        self.bf.close()
        print 't1 backup done set:',time.ctime()
        
    def currentHtml(self):
        return self.ie.Document.body.outerHTML
            
    def	getPageText(self,url):
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
        fname = re.compile(r'fname=(.*?)&').search(html)
        if fname != None:
            wb_cnt = re.compile(r'tagweibo[^>]*>[^>]*>(\d+)<').search(html).group(1)
            fans_cnt = re.compile(r'tagfans[^>]*>[^>]*>(\d+)<').search(html).group(1)
            follow_cnt = re.compile(r'tagfollow[^>]*>[^>]*>(\d+)<').search(html).group(1)
            return fname.group(1),follow_cnt,fans_cnt,wb_cnt
        '''
        fname = re.compile(r'title_big..[\n](.*?)[\n]').search(html)
        if fname != None:
            cseg = re.compile(r'strong>(\d+)<').findall(html)
            self.preUrl = 'http://e.weibo.com/'
            return '#e#'+fname.group(1),cseg[0],cseg[2],cseg[4]
        '''
        #retry
        return '##',0,0,0
    
    def getIdContent(self,uid):
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
        if int(wb_cnt) > 500:
            #self.getIdOriContent(uid,id_cnts)
            wb_cnt = 520
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
			
    def loadIdFilesToSet(self,uid_files,done_file,d='F:\\IS10\\grad\\data\\'):
        uid_file_paths = [d+f for f in uid_files]
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

    def writeIdContent(self,uid,d='F:\\IS10\\grad\\data\\'):
        #self.data_dir+str(uid)
        fh = open(d+str(uid),'w')
        cnt,text = self.getIdContent(uid)
        fh.writelines(cnt[0].encode('utf-8')+' '+' '.join(str(c) for c in cnt[1:]))
        fh.write(text.encode('utf-8'))
        fh.close()
        self.done_content_set.add(uid)#''.join([str(uid),'||',cnt[0].encode('utf-8')]))
        #modify_after_each_crawl uids+nick

		
def runIdCraw(url='http://weibo.com/10pku'):
    rpm = RoiPamie()
    rpm.initSets()
    if len(rpm.doing_set)<2 and len(rpm.collector_set)<2:
        rpm.openFullPage(url)
        html = rpm.currentHtml()
        rpm.doing_set = rpm.getIdsOnePage(html)
    print 'sdoing',str(len(rpm.doing_set))
    
    while len(rpm.collected_set)+len(rpm.collector_set)+len(rpm.doing_set)<100000:
        if len(rpm.doing_set)<=1 and len(rpm.collector_set)>1:
            rpm.collector_set,rpm.doing_set = rpm.doing_set,rpm.collector_set
        for i in rpm.doing_set:
            rpm.collected_set.add(i)
            rpm.getIdPage(i) #weak diversity if crawling all pages
            rpm.backupMem()
        rpm.doing_set = set()
    rpm.backupMem()


def runCtnCraw():
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
   

    
