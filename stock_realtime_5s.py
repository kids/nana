#coding=utf-8
import os
import time
from multiprocessing.dummy import Pool
import urllib2
import thread

url_head = 'http://hq.sinajs.cn/list='
ids_list = []
fh_dic = {}

def bkup_cffex_crawler():
    #coding=gbk
    import os
    import datetime
    import urllib2
    import xml.etree.ElementTree as ET
    from lxml import etree


    url_head = 'http://www.cffex.com.cn/fzjy/mrhq/'
    url_tail = '/index.xml'
    now = datetime.date(2015,7,20)

    def f(url):
        handle = urllib2.urlopen(url,timeout=2)
        #tree = ET.parse(handle.read())
        tree = etree.parse(handle)
        root = tree.getroot()

        out = []
        for art in root:
            t = ','.join(map(str,[field.text for field in art]))
            out.append(t)
        return '\n'.join(out)

    with open('icifih.csv','w') as fh:
        # retro back to d days
        for d in range(500):
            dt = now-datetime.timedelta(d)
            dt = str(dt).replace('-','/').replace('/','',1)
            print dt
            url = url_head+dt+url_tail
            try:
                r = f(url)
            except:
                continue
            fh.write(r)
            fh.write('\n')



def bkup_yahoo_crawler():
    url_head = 'http://table.finance.yahoo.com/table.csv?s='
    sz = '.sz'
    sh = '.ss'
    id_list = []
    file_list = os.listdir('.')

    def get_id_list(f, appendix):
        with open(f,'r') as l:
            for line in l:
                try:
                    id_list.append(line.split()[1]+appendix)
                except:
                    print line
                    pass

    def f(s_code):
        url = url_head+s_code
        s_file = s_code+'.csv'
        if s_file in file_list:
            return
        handle = urllib2.urlopen(url,timeout=2)
        with open(s_file,'wb') as sf_handle:
            sf_handle.write(handle.read())
        handle.close()

        
    def main():
        get_id_list('sz.list', sz)
        get_id_list('sh.list', sh)
        for i in id_list:
            print i
            # if i[0] != '0' and i[0] != '3' and i[0] != '6':
            #   continue
            try:
                f(i)
            except:
                print 'error'
                pass




def get_fh_dic():
	for id_list in ids_list:
		print id_list
		for i in id_list.split(','):
			try:
				fh = open('data/'+i+'.csv','a+')
				fh_dic[i] = fh
			except:
				continue
			#print 'key:',i
	return fh_dic

def get_id_list(f, suffix):
	id_list = []
	with open(f,'r') as l:
		for line in l:
			if line:
				id_list.append(suffix+line.split()[1])
				l = len(id_list)
	for i in range(6):
		ids = ','.join(id_list[l*i/6:l*(i+1)/6])
		ids_list.append(ids)


def http_get(url_body):
	url = url_head+url_body
	# print url
	print 'Loaded'
	try:
		handle = urllib2.urlopen(url,timeout=1)
		stk_t = handle.read()
	except:
		print 'error open url'
		return
	
	stk_t = stk_t.replace('"','').replace(';','').split('\n')
	try:
		print stk_t[0].split(',')[3]
	except:
		print stk_t[0]
	if len(stk_t):
		return stk_t


def get_time():
	#in float
	tm = time.ctime().split()
	wkd = tm[0]
	tm = tm[-2].split(':')
	tm_h = int(tm[0])
	tm_m = int(tm[1])
	tm = tm_h + tm_m/60.0
	return wkd, '%.2f'%tm

def process_http_response(id_list):
	rt_s = http_get(id_list)
	for i in rt_s:
		if len(i):
			i = i.split('=')
			sid = i[0].split('_')[-1]
			fh_dic[sid].write(i[1])
			close_fh()

def pool_process():
	pool = Pool(2)
	print 'Pooled'
	pool.map(process_http_response, ids_list)
	pool.close()
	pool.join()

def close_fh():
	for i in fh_dic:
		fh_dic[i].close()

def postprocess():
	sid_record_dict = {}
	# get_fh_dic()
	with open('tmp.csv','r') as fh:
		print 'processing log'
		
		for line in fh.readlines():
			try:
				sid, sdata = line.split('=')
				sid = sid.split('_')[-1]
			except:
				continue
			if sdata:
				sdata = ','.join(sdata.replace('"','').replace(';','').split(',')[1:])
				sid_record_dict[sid] = sid_record_dict.get(sid,[])
import os
import time
import urllib2

url_head = 'http://hq.sinajs.cn/list='
ids_list = []

def get_id_list(f, suffix):
    id_list = []
    with open(f,'r') as l:
        for line in l:
            if line:
                id_list.append(suffix+line.split()[1])
                l = len(id_list)
    for i in range(6):
        ids = ','.join(id_list[l*i/6:l*(i+1)/6])
        ids_list.append(ids)

def http_get(url_body):
    url = url_head+url_body
    # print url
    try:
        handle = urllib2.urlopen(url,timeout=1)
        stk_t = handle.read()
    except:
        print '[WARNING],step=[http_get],error open url'
        return

    stk_t = stk_t.replace('"','').replace(';','').split('\n')
    try:
        price = stk_t[0].split(',')[3]
        if float(price) > 1000:
            print 'step=[http_get], at',price
    except:
        print stk_t[0],'not parsed'
    if len(stk_t):
        return stk_t

def get_time():
    #in float
    tm = time.ctime().split()
    wkd = tm[0]
    tm = tm[-2].split(':')
    tm_h = int(tm[0])
    tm_m = int(tm[1])
    tm = tm_h + tm_m/60.0
    return wkd, '%.2f'%tm

def postprocess(f):
    sid_record_dict = {}
    print 'processing log'
    with open(f,'r') as fh:

        for line in fh.readlines():
            try:
                sid, sdata = line.split('=')
                sid = sid.split('_')[-1]
            except:
                continue
            if sdata:
                sdata = ','.join(sdata.replace('"','').replace(';','').split(',')[1:])
                sid_record_dict[sid] = sid_record_dict.get(sid,[])
                sid_record_dict[sid].append(sdata)

    for sid in sid_record_dict:
        try:
            with open('data/'+sid+'.csv','a+') as fh:
                fh.write(''.join(sid_record_dict[sid]))
        except:
            continue
    print 'step=[postprocess],',f,'finished at ',time.ctime()
    os.remove(f)


def main():
    get_id_list('sh.list', 'sh')
    get_id_list('sz.list', 'sz')
    print 'step=[main],Ids_list updated,len=',len(ids_list)

    while(1):
        wkd, tm = get_time()
        tm = float(tm)
        tm_i = int(tm/0.5)
        if wkd=='Sat' or wkd=='Sun' or tm<9.5:
            time.sleep(300)
            continue
        if tm< 11.5 or 13.0<tm<15.0:
            with open('tmp'+str(tm_i),'a+') as fh:
                for id_list in ids_list:
                    html = http_get(id_list)
                    if html:
                        fh.write('\n'.join(html))
                print 'step=[main],updated data at',time.ctime()
                time.sleep(3)
        else:
            for i in range(19,30):
                if 'tmp'+str(i) in os.listdir('.'):
                    postprocess('tmp'+str(i))
            time.sleep(300)

if __name__=='__main__':
    main()
