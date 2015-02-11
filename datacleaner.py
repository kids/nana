#coding=utf-8

import re
import os
import time

class Cleaner:
    def removeDuplicateLine(self,filetext):
        lineSet = set()
        for line in filetext.split('\n'):
            lineSet.add(line.strip())
        return '\n'.join(list(lineSet))

    def removeWeiboAt(self,filetext):
        return re.compile(r'@.*?\s').sub(' ',filetext)

    def weiboCln(self,filename):
        clner = Cleaner()
        filein = open('F:\\IS10\\grad\\data\\'+filename,'r')
        fileout = open('F:\\IS10\\grad\\cata\\'+filename,'w')
        tx = clner.removeDuplicateLine(filein.read())
        tx = clner.removeWeiboAt(tx)
        fileout.write(tx)
        fileout.close()
        filein.close()
        
    def removeWMFrame(self,page):
        rp = re.compile(r'站内信件(.*?)大作中提到').search(page)
        if rp:
            return rp.group(1)
        else:
            rp = re.compile(r'站内信件(.*?)※ 来源').search(page)
        if rp:
            return rp.group(1)
        else:
            return ''

    def removeMultipl(self,filetext):
        pass

    def divideFile(self,filename):
        filein = open('F:\\IS10\\grad\\fata\\'+filename,'r')
        fileo1 = open('F:\\IS10\\grad\\fata\\'+filename+'A','w')
        fileo2 = open('F:\\IS10\\grad\\fata\\'+filename+'B','w')
        f = filein.read().split('\n')
        for i,j in enumerate(f):
            if i<len(f)/2.0:
                fileo1.write(j+'\n')
            else:
                fileo2.write(j+'\n')
        fileo1.close()
        fileo2.close()
        filein.close()
        
def runWeiboCln():
    clner = Cleaner()
    for f in os.listdir('F:\\IS10\\grad\\data'):
        if f.startswith(('1','2','3')):
            clner.weiboCln(f)
    

def cleanwmboard():
    clner = Cleaner()
    filein = open('F:\\IS10\\grad\\data\\ASTWT','r')
    fileout = open('F:\\IS10\\grad\\cata\\tmpw.txt','w')
    for line in filein.readlines():
        print 'L0',line
        line = clner.removeWMFrame(line)
        print line
        fileout.writeline(line)
    fileout.close()
    filein.close()

import redis
def cleanredis():
    r = redis.StrictRedis()
    f1 = open('F:\\IS10\\grad\\data\\redis-once','a')
    f2 = open('F:\\IS10\\grad\\data\\redis-twice','a')
    f3 = open('F:\\IS10\\grad\\data\\redis-lessten','a')
    for i in range(1000000):
        if i%100000==0:
            print time.ctime(),str(i)
        k = r.randomkey()
        if len(k.split()[0])<4 or len(k.split()[1])<4:
            r.delete(k)
            continue
        v = r.get(k)
        if int(v)>9:
            continue
        if v=='1':
            print>>f1, k
            r.delete(k)
            continue
        if v=='2':
            print>>f2, k
            r.delete(k)
            continue
        print>>f3, k+' '+v
        r.delete(k)
    f1.close()
    f2.close()
    f3.close()

def rundivide():
    clner = Cleaner()
    for f in os.listdir('F:\\IS10\\grad\\fata'):
        clner.divideFile(f)
    
def lambdo():
    d=dict()
    r = redis.StrictRedis()
    f1 = open('F:\\IS10\\grad\\data\\redis-lessten','r')
    #f2 = open('F:\\IS10\\grad\\data\\cnt-wb-euid','w')
    for l in f1.readlines():
        l = l.split()
        if len(l[0])>3 and len(l[1])>3:
            pass
    #f2.close()
    f1.close()
    
if __name__ == '__main__':
    rundivide()
