#coding=utf-8

import os
import sys
import time
import redis

class Counter:
    def cntWord(self,filetext):
        dc = dict()
        stopset = set()
        fh = open('F:\\IS10\\grad\\data\\stopwd.txt','r')
        for w in fh.read().split('\n'):
            stopset.add(w)
        for line in filetext.split('\n'):
            for wd in line.split():
                if wd in stopset:
                    continue
                dc[wd] = dc.get(wd,0)+1
        return dc


    def cntfile(self,f):
        fn = 'F:\\IS10\\grad\\cata\\'+f
        ftext = open(fn).read()
        dc = self.cntWord(ftext)
        sortdic = sorted(dc.items(),key=lambda d:d[1],reverse=True)
        return ';'.join(','.join(str(l) for l in v) for v in sortdic)

    def cnttotal(self,statfile='F:\\IS10\\grad\\data\\wdcntall'):
        '''
            count words of all files
        '''
        fh = open(statfile,'w')
        dk = dict()
        for f in os.listdir('F:\\IS10\\grad\\cata'):
            if not f.startswith(('1','2','3')):
                continue
            f = open('F:\\IS10\\grad\\cata\\'+f)
            tk = self.cntWord(f.read())
            for i in tk:
                dk[i] = dk.get(i,0)+tk[i]
            f.close()
        sortdic = sorted(dk.items(),key=lambda d:d[1],reverse=True)
        fh.write('\n'.join(','.join(str(l) for l in v) for v in sortdic))
        fh.close()

    def paircnt(self,wdset):
        pairdict = dict()
        cdir = 'F:\\IS10\\grad\\cata'
        fileset = os.listdir(cdir)
        s = []
        for f in fileset:
            if f.startswith('A'):
                s.append(f)
        fileset = s
        rnd = 0
        for wd in wdset:
            print str(rnd+1),wd
            rnd += 1
            '''in test processing 40 words'''
            if rnd == 40:
                break
            for f in fileset:
                fh = open(cdir+'\\'+f)
                for line in fh.read().split('\n'):
                    #print line
                    sw = line.split()
                    #print 'sw',str(len(sw))
                    for i,w in enumerate(sw):
                        if w == wd:
                            for j in range(1,4):
                                if i+j == len(sw):
                                    break
                                if sw[i+j] in wdset:
                                    if w<sw[i+j]:
                                        pair = w+' '+sw[i+j]
                                    else:
                                        pair = sw[i+j]+' '+w
                                    pairdict[pair]=pairdict.get(pair,0)+1
                                    #print len(pairdict)
                fh.close()
        fo = open('F:\\IS10\\grad\\data\\tmpw.txt','w')
        for pair in pairdict:
            fo.write(' '.join([pair,str(pairdict[pair]),'\n']))
        fo.close()

    def pairdbcnt(self,wdset):
        r = redis.StrictRedis(host='127.0.0.1',port=6379)
        cdir = 'F:\\IS10\\grad\\cata'
        fileset = os.listdir(cdir)
        s = []
        for f in fileset:
            if f.startswith('A') and f>'AXinWenZX':
                s.append(f)
        fileset = s
        rnd = 0
        for f in fileset:
            fh = open(cdir+'\\'+f)
            print time.ctime(),'through',f
            for line in fh.read().split('\n'):
                sw = line.split()
                for i,w in enumerate(sw):
                    if w not in wdset:
                        sw[i] = ''
                if len(sw) > 4:
                    head4 = sw[:3]
                    for i in range(3,len(sw)):
                        if sw[i] != '':
                            for j in range(i-3,i):
                                if sw[j] != '':
                                    if sw[i]<sw[j]:
                                        pair = sw[i]+' '+sw[j]
                                    else:
                                        pair = sw[j]+' '+sw[i]
                                    if r.exists(pair):
                                        r.incr(pair)
                                    else:
                                        r.set(pair,1)
                else:
                    head4 = sw
                for i in range(1,len(head4)):
                    if sw[i] != '':
                        for j in range(0,i-1):
                            if sw[j] != '':
                                if sw[i]<sw[j]:
                                    pair = sw[i]+' '+sw[j]
                                else:
                                    pair = sw[j]+' '+sw[i]
                                if r.exists(pair):
                                    r.incr(pair)
                                else:
                                    r.set(pair,1)
                

            fh.close()
        
    def runwdcnt(self):
        '''
            count words in each file
        '''
        ct = Counter()
        folder = 'F:\\IS10\\grad\\cata'
        statfile = open('F:\\IS10\\grad\\data\\wdcnt','w')
        t = time.time()
        for f in os.listdir(folder):
            if not f.startswith(('1','2','3')):
                continue
            try:
                ctf = ct.cntfile(f)
                statfile.write(f+':')
                statfile.write(ctf)
                statfile.write('\n')
                print time.time()-t
            except:
                print sys.exc_info()[0],sys.exc_info()[1]
                statfile.flush()
        statfile.close()

    def wdset(self):
        '''read totalword set'''
        tset = set()
        fh = open('F:\\IS10\\grad\\data\\wdcntall','r')
        for w in fh.read().split('\n'):
            w = w.split(',')[0]
            if len(w)>2 and len(w)<15:
                tset.add(w)
        fh.close()
        '''read stopwd set'''
        stopset = set()
        fh = open('F:\\IS10\\grad\\data\\stopwd.txt','r')
        for w in fh.read().split('\n'):
            stopset.add(w)
        #print ''.join(list(stopset))
        fh.close()
        tset =  tset - stopset
        print 'load to wd set',str(len(tset))
        return tset

    def wdict(self):
        d = dict()
        f = open('F:\\IS10\\grad\\data\\tmp.txt','r')
        for l in f.readlines():
            p = l.split(',')
            d[p[0]] = p[1]
        f.close()
        return d

    def cnt_id_norm(self):
        f = open('F:\\IS10\\grad\\data\\cnt-wb-euid','r')
        fw = open('F:\\IS10\\grad\\data\\cnt-wb-uid','w')
        wd = self.wdict()
        for l in f.readlines():
            uid = l.split(':')[0]
            t = ':'.join(l.split(':')[1:])
            td = dict()
            for w in t.split(';'):
                w = w.split(',')
                if wd.has_key(w[0]):
                    td[w[0]] = '%.4f'%(float(w[1])/(int(wd[w[0]]))**0.5)
                else:
                    td[w[0]] = 0
            sortdic = sorted(td.items(),key=lambda d:d[1],reverse=True)
            fw.write(uid+':'+';'.join(','.join(str(l) for l in v) for v in sortdic)+'\n')
        fw.close()
        f.close()

def runpaircnt():
    ct = Counter()
    ct.paircnt(wdset())
    
def runtotal():
    ct = Counter()
    ct.cnttotal()

def rundbpair():
    ct = Counter()
    ct.pairdbcnt(wdset())

def runnormwbid():
    ct = Counter()
    ct.cnt_id_norm()
    
def lambdo():
    r=redis.StrictRedis()
    d=dict()
    f=open('F:\\IS10\\grad\\data\\tmpl.txt','w')
    for i in range(100000):
        k=r.randomkey()
        v=r.get(k)
        
        v=int(v)#/10
        if v>100:
            continue
        d[v]=d.get(v,0)+1
    for i in d:
        print>>f, i,d[i]
    f.close()

if __name__=='__main__':
    runnormwbid()
