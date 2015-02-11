#coding=utf-8

import redis
import math
import time
import random


class Clustering:
    #f = open('F:\\IS10\\grad\\data\\corre-70','w')
    #f2 = open('F:\\IS10\\grad\\data\\corre-35','w')
    f7 = open('F:\\IS10\\grad\\data\\corre-uid','a')
    def correlate(self,objA,objB):
        #correDict = dict()
        l = []
        r = redis.StrictRedis(host='127.0.0.1',port=6379)
        for oba in objA:
            for obb in objB:
                if oba == obb:
                    l.append(1)
                    continue
                if oba < obb:
                    pair = oba+' '+obb
                else:
                    pair = obb+' '+oba
                if r.exists(pair):
                    l.append(math.log(float(r.get(pair)))/10)
                #correDict[pair] = r.get(pair)
        #print len(l)
        dxy = (1-sum(l)/150) #2500 is max combinatrics as C(2,70)=2415
        self.f7.write(str(dxy))
        self.f7.write('\n')
        #sortdic = sorted(correDict.items(),key=lambda d:int(d[1]),reverse=True)
        #print ';'.join(','.join(str(l) for l in v) for v in sortdic)
        #print len(correDict)
        '''f = open('F:\\IS10\\grad\\data\\tmpl.txt','w')
        for p in sortdic:
            if int(p[1])>1000:
                print>>f, ','.join(p)
        '''

    def corre(self,objA,objB):
        l = []
        r = redis.StrictRedis(host='127.0.0.1',port=6379)
        for oba in objA:
            for obb in objB:
                if oba == obb:
                    l.append(1)
                    continue
                if oba < obb:
                    pair = oba+' '+obb
                else:
                    pair = obb+' '+oba
                if r.exists(pair):
                    l.append(math.log(float(r.get(pair)))/10)
        return l

    def correlate2(self,objA,objB):
        l = self.corre(objA[:35],objB[:35])
        l1 = self.corre(objA[35:],objB[35:])
        l = l+l1
        dxy = (1-sum(l)/150)
        #self.f7.write(str(dxy))
        #self.f7.write('\n')

    def correlate7(self,objA,objB):
        l = []
        for i in range(5):
            l += self.corre(objA[(i*20):((i+1)*20-1)],objB[(i*20):((i+1)*20-1)])
            dxy = (1-sum(l)/150)
        self.f7.write(str(dxy))
        self.f7.write('\n')

    def cluster(self,r):
        '''
            extract pair correlations in fh
            to be clusters
        '''
        fh = open('F:\\IS10\\grad\\data\\corre-70','r')
        clusters = []
        for line in fh.readlines():
            line = line.split(',')
            if float(line[2])<r:
                clusters.append(set((line[0],line[1])))
        ctemp = clusters
        clusters = []
        while ctemp:
            tset = ctemp[0]
            ctemp.remove(ctemp[0])
            i = 0
            while i<len(ctemp):
                if tset&ctemp[i]:
                    tset = tset|ctemp[i]
                    ctemp.remove(ctemp[i])
                else:
                    i += 1
            clusters.append(tset)
        fh.close()
        print len(clusters)

    def loadvdict(self):
        fh = open('F:\\IS10\\grad\\data\\tmp.txt','r')
        d = dict()
        i = 0
        for w in fh.read().split('\n'):
            w = w.split(',')[0]
            if len(w)>3:
                d[w]=i
                i+=1
        fh.close()
        return d #len(d)=42100
        
    def vectorize(self,vdict):
        fh = open('F:\\IS10\\grad\\data\\tmpw.txt','r')
        vmatrics = []
        for line in fh.readlines():
            l = [0]*42100
            lineid = line.split(':')[0]
            line = ''.join(line.split(':')[1:])
            for i in line.split(';'):
                i = i.split(',')
                if i[0] in vdict:
                    l[vdict[i[0]]]=i[1]
            vmatrics.append((lineid,l))
        return vmatrics
        
    def cosinel(self,l1,l2):
        xy = 0
        x = 0
        y = 0
        for i in range(42100):
            xy += float(l1[i])*float(l2[i])
            x += float(l1[i])**2
            y += float(l2[i])**2
        x = x**0.5
        y = y**0.5
        return xy/(x*y)
        
    def kmeans(self,k):
        vdict = self.loadvdict()
        vmatrics = self.vectorize(vdict)
        centroid = []
        for i in range(k):
            i = random.randint(0,len(vmatrics)-1)
            centroid.append(([vmatrics[i][0]],vmatrics[i][1]))
            vmatrics.remove(vmatrics[i])
        for i in vmatrics:
            minimal = 10
            for j,c in enumerate(centroid):
                cosl = self.cosinel(c[1],i[1])
                if cosl < minimal:
                    minimal = cosl
                    k = j
            centroid[k][0].append(i[0])
            for o in range(42100):
                centroid[k][1][o] = (float(centroid[k][1][o])+float(i[1][o]))/2.0
        print centroid[0][0],centroid[1][0]
    
    import numpy
    def umatrix(self):
        m = []
        l = []
        return m
    def eigen(self):
        eigenvalue = []
        eigenvector = []
        a = numpy.arange(16)
        a=a.reshape(4,4)
        b,c,d = numpy.linalg.svg(a)
        print b,'#',c,'#',d
        print eigenvalue
        return eigenvector
    def spectrum(self,k):
        pass
        
    def loadObjSet(self,wdset,line):
        '''
            load a line of word count set for a uid
            turn to a dict or select to set?
        '''
        uid = line.split(':')[0]
        self.f7.write(uid+',')
        ulist = (''.join(line.split(':')[1:])).split(';')
        #print uid,'has',str(len(ulist)),'words in set'
        objlist = []
        for wcnt in ulist:
            wcnt = wcnt.split(',')
            if wcnt[0] in wdset:
                objlist.append(wcnt[0])
        #print str(len(objlist)),'in word space'
        #print ','.join(objlist)
        '''select attribute to make set'''
        return objlist

def runsingle():
    fh = open('F:\\IS10\\grad\\data\\cnt-wb-uid','r')
    lines = fh.read().split('\n')
    fh.close()
    tset = set()
    fh = open('F:\\IS10\\grad\\data\\tmp.txt','r')
    for w in fh.read().split('\n'):
        w = w.split(',')[0]
        tset.add(w)
    fh.close()

    c = time.time()
    cl = Clustering()
    for i in range(100,500)+range(2000,2200): #5432
        k=2101
        if i>2101:
            k=i
        if i%10==0:
            print str(i),'round processing'
        for j in range(3000,3200)+range(4000,4200):
            #obj1 = cl.loadObjSet(tset,lines[random.randint(0,5000)])[:120]
            obj1 = cl.loadObjSet(tset,lines[i])[:50]
            obj2 = cl.loadObjSet(tset,lines[j])[:50]
            #print ' '.join(obj1)
            cl.correlate(obj1,obj2)
        print time.time()-c
        cl.f7.flush()
    cl.f7.close()

def runcluster():
    cl = Clustering()
    cl.cluster(0.9)

def runkmeans():
    cl = Clustering()
    cl.kmeans(2)

def run():
    cl = Clustering()
    cl.eigen()
    
if __name__=='__main__':
    run()
