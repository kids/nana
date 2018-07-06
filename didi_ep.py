#coding=utf-8
import os
import time
import json
import socket
from urllib2 import urlopen


def pddata():
    import pandas as pd

    _ar = 6

    os.chdir('f://p//qsmodel//data')

    f1='000001.ss.csv'
    f2='000001.sz.csv'

    a1=pd.read_csv(f1,index_col=0)[[-1]]
    a2=pd.read_csv(f2,index_col=0)[[-1]]

    for p in range(1,_ar):
        a1 = pd.concat([a1,a2.shift(-p)],axis=1)

    r = pd.ols(y=a1[[0]],x=[[1,2,3,4]])

    print r


#os.chdir('f://a//soso')
def getbd09(lon,lat):
    url0='http://api.map.baidu.com/geoconv/v1/?coords='
    url1='&from=1&to=5&ak=Mv6GpDpEey22Ir7BsbmRRxaT'
    url=url0+','.join(map(str,[lon,lat]))+url1
    r = urllib2.urlopen(url,timeout=1).read()
    r = json.loads(r)['result'][0]
    return [r['x'],r['y']]


def blktrans(from_f='processed_log',to_f='processed_log_'):
    f = open(to_f, 'w+')
    with open(from_f,'r') as fo:
        for l in fo.readlines():
            if l.find('blk')>1:
                l=l.split()
                for i in range(len(l)):
                    if l[i].startswith('blk'):
                        lonlat=l[i].split(',')
                        lon=float(lonlat[0][5:])/10000
                        lat=float(lonlat[1][:-1])/10000
                        print 'debug: lon, lat',lon,lat
                        lonlat=','.join(map(str,getbd09(lon,lat)))
                        l[i]='blk=['+lonlat+']'
                l=' '.join(l)
            f.write(l+'\n')
    f.close()


def batchtrans():
    import gps_coordinates_transformer as EvilTransform
    a='''
    1163072,399812,40.231386
    1163073,399811,42.121669
    1163072,399813,38.023371
    1163073,399810,42.164086
    1163071,399810,25.930479
    1163076,399808,37.449225
    1163074,399809,41.731928
    1163072,399811,42.222955
    1163074,399810,42.774614
    '''
    #39.985390,116.321515
    for i in a.split('\n'):
        if not i:
            continue
        lon,lat,s=i.split(',')
        print ','.join(map(str,EvilTransform.transform_wgs2mars(float(lat),float(lon))))

    c=(1163073,399809,38.599020)
    for i in a.split('\n'):

        if not i:
            continue
        print 'c',','.join(map(str,c))
        print 'i',i
        x,y,s=i.split(',')
        x=(int(x)*float(s)+c[0]*c[2])/(float(s)+c[2])
        y=(int(y)*float(s)+c[1]*c[2])/(float(s)+c[2])
        c=(int(x),int(y),float(s)+c[2])

    d={}
    with open('zhongguancun-log.txt','r') as f:
        for l in f.read().split('\n'):
            if l.find('level')>0:
                l=l.split('||')[0].split()[-1]
                try:
                    l=json.loads(l)
                    l=[i['level'] for i in l['wifis']]
                    print sorted(l,reverse=True)
                    if len(l) in d:
                        d[len(l)]+=1
                    else:
                        d[len(l)]=1
                except:
                    pass
        print d


def errlr(coef=[3]):
    learn_size=2200
    pred_size=600
    import numpy as np
    from sklearn import linear_model
    f=np.genfromtxt('part-00000.csv',delimiter=',')
    y=f[:learn_size,2]
    y=np.array(y).reshape(learn_size,1)
    #f[:,3]=[1.0/i for i in f[:,3]]
    x=f[:learn_size,4]
    tx=f[learn_size:learn_size+pred_size,3]
    for i in coef:
        x=np.vstack([x,f[:learn_size,i]])
        tx=np.vstack([tx,f[learn_size:learn_size+pred_size,i]])
    #x=np.array(x).reshape(learn_size,-1)
    #tx=np.array(tx).reshape(pred_size,-1)
    x=x.transpose()
    tx=tx.transpose()
    ty=f[learn_size:learn_size+pred_size,2]
    ty=np.array(ty).reshape(pred_size,1)
    #np.linalg(X,y)
    regr = linear_model.Ridge(alpha=0.9)
    regr.fit(x, y)
    print regr.intercept_, regr.coef_
    pred = regr.predict(tx)

    #pred=f[learn_size:learn_size+pred_size,3]
    #pred=[i-30 for i in pred]
    print sum(ty)/pred_size,sum(pred)/pred_size
    print 'squared err:',pow(sum([(ty[i]-pred[i])**2 for i in range(pred_size)])/pred_size,0.5)
    print ty.transpose()[0][:20]
    print pred.transpose()[0][:20]


def extract():
    board=[[[116.311719,40.036174],[116.312191,40.036014 ],[116.311821,40.035612],[116.311403,40.035764]],
[[116.311451,40.035349],[116.312025,40.035456 ],[116.312197,40.035037],[116.311591,40.034918]],
[[116.311961,40.03371],[ 116.312138,40.033747 ],[116.31232,40.033221],[ 116.312127,40.033197]],
[[116.312712,40.032646],[116.313366,40.032786 ],[116.313415,40.032646],[116.312755,40.032511]],
[[116.311564,40.029336],[116.311741,40.028021 ],[116.310829,40.027935],[116.310647,40.029258]]]
    for i in board:
        lat=[x[0] for x in i]
        lon=[x[1] for x in i]
        print min(lat),max(lat),min(lon),max(lon)

def cell():
    ocell='''46000,4278,19624
46000,4278,22044932
46000,4278,19624
46000,4278,24220673
46000,4278,23658497
46000,4284,17660417'''
    pcell=ocell.split('\n')
    pcell=list(set(pcell))
    for i in pcell:
        a,b,c=i.split(',')
        b=hex(int(b))[2:]
        c=hex(int(c))[2:]
        b=''.join(['0']*(4-len(b)))+b
        c=''.join(['0']*(8-len(c)))+c
        print a+b+c

def toppoi():
    a=[["梅花园", 3690], ["文冲地铁站", 3255], ["三元里地铁站", 5124], ["邦华环球广场", 3358], ["广东省中医院", 8407], ["万菱汇", 5101], ["坑口地铁站", 3495], ["猎德村复建房(5区)", 5442], ["东圃", 3338], ["广东省汽车客运站", 3479], ["长湴地铁站", 6293], ["广州军区广州总医院", 3255], ["时代广场", 4444], ["欣荣宏·国际商贸城", 5493], ["广州北站", 3080], ["中山大学附属第三医院天河院区", 3359], ["太阳新天地", 4348], ["花都区大润发", 3689], ["体育西路地铁站", 3432], ["棠德花苑", 3103], ["广州市妇女儿童医疗中心", 3492], ["广州东火车站", 3019], ["高德置地广场", 3021], ["海珠广场", 3348], ["广州东站地铁站", 3400], ["东方宝泰购物广场", 3307], ["万达百货(广州白云店)", 3626], ["白云区新市街道机场路新市墟", 4170], ["西城都荟", 3237], ["中海康城花园", 3106], ["银座酒店", 3217], ["广州市第一人民医院", 3644], ["车陂南", 3297], ["黄村地铁站", 6524], ["广州医科大学第一附属医院", 3139], ["龙归地铁站", 5097], ["南方医院", 4398], ["广州白云国际机场", 8526], ["天河客运站", 10621], ["人和地铁站", 8808], ["萝岗万达广场", 3298], ["中华广场", 6331], ["江南西", 9516], ["车陂", 3557], ["广州城建职业学院", 3687], ["嘉禾望岗", 3838], ["江南新地", 3763], ["广州东站", 18813], ["洛溪地铁站", 3802], ["万达广场", 6981], ["广州南站", 24476], ["天河区天河客运站", 4309], ["番禺宾馆", 3400], ["东汇城", 3967], ["上下九广场", 3189], ["金碧新城", 3961], ["员村地铁站", 3015], ["番禺广场", 11521], ["大塘地铁站", 3070], ["新市墟", 6441], ["广州南火车站", 7163], ["汉溪长隆地铁站", 5084], ["岑村小学", 3093], ["保利花园", 4030], ["厦滘地铁站", 3610], ["广州市儿童医院", 3477], ["利通广场", 3951], ["猎德花园", 4080], ["翠城花园", 3549], ["大润发", 4037], ["珠江新城", 7372], ["北京路", 3976], ["富力中心", 3567], ["岭南新世界", 4150], ["来又来时尚购物广场", 4728], ["广州信息港", 4942], ["乐峰广场", 5522], ["中山大学附属第一医院", 4345], ["白云国际机场航站楼", 5185], ["同和地铁站", 4485], ["奥园广场", 7380], ["中石化大厦", 5482], ["同和", 4620], ["从化汽车站", 5848], ["维多利广场", 3558], ["广州国际金融中心", 3365], ["番禺中心医院", 5893], ["正佳广场", 9561], ["星汇园", 3554], ["汇侨新城", 4944], ["金城广场", 4237], ["五羊新城", 4417], ["番禺广场地铁站", 6866], ["珠江帝景苑", 3276], ["大石地铁站", 3211], ["城启·荔港南湾", 3623], ["新造地铁站", 3867], ["骏景花园", 3083], ["猎德村复建房(1区)", 3378], ["从城大道28从化汽车站", 3230], ["白云区白云机场", 3016], ["万国广场", 4704], ["市桥地铁站", 10610], ["江夏地铁站", 3796], ["光大花园", 3033], ["万达广场(萝岗店)", 3195], ["白云机场", 14840], ["广州塔", 3030], ["中华国际中心", 3819], ["太古汇", 9875], ["岗顶", 5392], ["广百新一城", 3179], ["东峻广场", 3362], ["广州火车站", 11647], ["岗顶地铁站", 3601], ["广东财经大学", 5160], ["广东省人民医院", 6761], ["花城汇", 4001], ["暨南大学", 3123], ["富力桃园", 3880], ["沙河顶", 3442], ["芳村地铁站", 3800], ["中环广场", 5220], ["广园客运站", 5863], ["三元里", 5085], ["广州银行大厦", 5714], ["祈福新村", 4247], ["天河城", 4589]]
    for i in sorted(a,key=lambda k:k[1],reverse=True):
        print i[0],i[1]

def diffpoi():
    a=[["花都区大润发", 3643], ["5号停机坪购物广场", 3487], ["广州东站地铁站", 3073], ["东方宝泰购物广场", 3111], ["万达百货(广州白云店)", 4086], ["白云区新市街道机场路新市墟", 3223], ["西城都荟", 3603], ["黄村地铁站", 5101], ["广东金融学院", 3447], ["龙归地铁站", 3869], ["广州白云国际机场", 5109], ["人和地铁站", 7365], ["天河客运站", 8525], ["萝岗万达广场", 3599], ["中华广场", 4297], ["江南西", 6617], ["广州城建职业学院", 4447], ["江南新地", 3027], ["广州东站", 13512], ["万达广场", 6600], ["广州南站", 16614], ["天河区天河客运站", 3283], ["东汇城", 4279], ["番禺广场", 7640], ["新市墟", 4863], ["广州南火车站", 6383], ["汉溪长隆地铁站", 3412], ["保利花园", 3370], ["大润发", 4717], ["珠江新城", 4122], ["北京路", 3743], ["岭南新世界", 3082], ["来又来时尚购物广场", 6195], ["乐峰广场", 6416], ["白云国际机场航站楼", 3416], ["同和地铁站", 4009], ["奥园广场", 7818], ["同和", 3317], ["从化汽车站", 6411], ["正佳广场", 8428], ["汇侨新城", 3169], ["金城广场", 3893], ["番禺广场地铁站", 4318], ["从城大道28从化汽车站", 3362], ["万国广场", 5277], ["市桥地铁站", 7691], ["万达广场(萝岗店)", 3490], ["白云机场", 8417], ["太古汇", 7164], ["岗顶", 3679], ["广州火车站", 8228], ["广东财经大学", 3730], ["中环广场", 3430], ["广园客运站", 4022], ["三元里", 3669], ["祈福新村", 3100], ["天河城", 4989]]
    b=[["梅花园", 3690], ["文冲地铁站", 3255], ["三元里地铁站", 5124], ["邦华环球广场", 3358], ["广东省中医院", 8407], ["万菱汇", 5101], ["坑口地铁站", 3495], ["猎德村复建房(5区)", 5442], ["东圃", 3338], ["广东省汽车客运站", 3479], ["长湴地铁站", 6293], ["广州军区广州总医院", 3255], ["时代广场", 4444], ["欣荣宏·国际商贸城", 5493], ["广州北站", 3080], ["中山大学附属第三医院天河院区", 3359], ["太阳新天地", 4348], ["花都区大润发", 3689], ["体育西路地铁站", 3432], ["棠德花苑", 3103], ["广州市妇女儿童医疗中心", 3492], ["广州东火车站", 3019], ["高德置地广场", 3021], ["海珠广场", 3348], ["广州东站地铁站", 3400], ["东方宝泰购物广场", 3307], ["万达百货(广州白云店)", 3626], ["白云区新市街道机场路新市墟", 4170], ["西城都荟", 3237], ["中海康城花园", 3106], ["银座酒店", 3217], ["广州市第一人民医院", 3644], ["车陂南", 3297], ["黄村地铁站", 6524], ["广州医科大学第一附属医院", 3139], ["龙归地铁站", 5097], ["南方医院", 4398], ["广州白云国际机场", 8526], ["天河客运站", 10621], ["人和地铁站", 8808], ["萝岗万达广场", 3298], ["中华广场", 6331], ["江南西", 9516], ["车陂", 3557], ["广州城建职业学院", 3687], ["嘉禾望岗", 3838], ["江南新地", 3763], ["广州东站", 18813], ["洛溪地铁站", 3802], ["万达广场", 6981], ["广州南站", 24476], ["天河区天河客运站", 4309], ["番禺宾馆", 3400], ["东汇城", 3967], ["上下九广场", 3189], ["金碧新城", 3961], ["员村地铁站", 3015], ["番禺广场", 11521], ["大塘地铁站", 3070], ["新市墟", 6441], ["广州南火车站", 7163], ["汉溪长隆地铁站", 5084], ["岑村小学", 3093], ["保利花园", 4030], ["厦滘地铁站", 3610], ["广州市儿童医院", 3477], ["利通广场", 3951], ["猎德花园", 4080], ["翠城花园", 3549], ["大润发", 4037], ["珠江新城", 7372], ["北京路", 3976], ["富力中心", 3567], ["岭南新世界", 4150], ["来又来时尚购物广场", 4728], ["广州信息港", 4942], ["乐峰广场", 5522], ["中山大学附属第一医院", 4345], ["白云国际机场航站楼", 5185], ["同和地铁站", 4485], ["奥园广场", 7380], ["中石化大厦", 5482], ["同和", 4620], ["从化汽车站", 5848], ["维多利广场", 3558], ["广州国际金融中心", 3365], ["番禺中心医院", 5893], ["正佳广场", 9561], ["星汇园", 3554], ["汇侨新城", 4944], ["金城广场", 4237], ["五羊新城", 4417], ["番禺广场地铁站", 6866], ["珠江帝景苑", 3276], ["大石地铁站", 3211], ["城启·荔港南湾", 3623], ["新造地铁站", 3867], ["骏景花园", 3083], ["猎德村复建房(1区)", 3378], ["从城大道28从化汽车站", 3230], ["白云区白云机场", 3016], ["万国广场", 4704], ["市桥地铁站", 10610], ["江夏地铁站", 3796], ["光大花园", 3033], ["万达广场(萝岗店)", 3195], ["白云机场", 14840], ["广州塔", 3030], ["中华国际中心", 3819], ["太古汇", 9875], ["岗顶", 5392], ["广百新一城", 3179], ["东峻广场", 3362], ["广州火车站", 11647], ["岗顶地铁站", 3601], ["广东财经大学", 5160], ["广东省人民医院", 6761], ["花城汇", 4001], ["暨南大学", 3123], ["富力桃园", 3880], ["沙河顶", 3442], ["芳村地铁站", 3800], ["中环广场", 5220], ["广园客运站", 5863], ["三元里", 5085], ["广州银行大厦", 5714], ["祈福新村", 4247], ["天河城", 4589]]
    a=[i[0] for i in a]
    b=[i[0] for i in b if i[1]>4000]
    a=set(a)
    b=set(b)
    inter=a.intersection(b)
    print len(inter)
    for i in inter:
        print i
    asub=a-b
    print len(asub)
    for i in asub:
        print i
    bsub=b-a
    print len(bsub)
    for i in bsub:
        print i


class HMM:
    def __init__(self, Ann, Bnm, pi1n):
        pass
    
    def BaumWelch(self,L,T,O,alpha,beta,gamma):
        print "BaumWelch"
        DELTA = 0.01 ; round = 0 ; flag = 1 ; probf = [0.0]
        delta = 0.0 ; deltaprev = 0.0 ; probprev = 0.0 ; ratio = 0.0 ; deltaprev = 10e-70
        
        xi = np.zeros((T,self.N,self.N))
        pi = np.zeros((T),np.float)
        denominatorA = np.zeros((self.N),np.float)
        denominatorB = np.zeros((self.N),np.float)
        numeratorA = np.zeros((self.N,self.N),np.float)
        numeratorB = np.zeros((self.N,self.M),np.float)
        scale = np.zeros((T),np.float)
        
        while True :
            probf[0] = 0
            # E - step
            for l in range(L):
                self.ForwardWithScale(T,O[l],alpha,scale,probf)
                self.BackwardWithScale(T,O[l],beta,scale)
                self.ComputeGamma(T,alpha,beta,gamma)
                self.ComputeXi(T,O[l],alpha,beta,gamma,xi)
                for i in range(self.N):
                    pi[i] += gamma[0,i]
                    for t in range(T-1): 
                        denominatorA[i] += gamma[t,i]
                        denominatorB[i] += gamma[t,i]
                    denominatorB[i] += gamma[T-1,i]
                    
                    for j in range(self.N):
                        for t in range(T-1):
                            numeratorA[i,j] += xi[t,i,j]
                    for k in range(self.M):
                        for t in range(T):
                            if O[l][t] == k:
                                numeratorB[i,k] += gamma[t,i]
                            
            # M - step
            for i in range(self.N):
                self.pi[i] = 0.001/self.N + 0.999*pi[i]/L
                for j in range(self.N):
                    self.A[i,j] = 0.001/self.N + 0.999*numeratorA[i,j]/denominatorA[i]
                    numeratorA[i,j] = 0.0
                
                for k in range(self.M):
                    self.B[i,k] = 0.001/self.M + 0.999*numeratorB[i,k]/denominatorB[i]
                    numeratorB[i,k] = 0.0
                
                pi[i]=denominatorA[i]=denominatorB[i]=0.0;
            
            if flag == 1:
                flag = 0
                probprev = probf[0]
                ratio = 1
                continue
            
            delta = probf[0] - probprev
            ratio = delta / deltaprev
            probprev = probf[0]
            deltaprev = delta
            round += 1
            
            if ratio <= DELTA :
                print "num iteration ",round
                break
         
def latlon2poi(p,host='gaode'):
# reverse geo coding
    socket.setdefaulttimeout(10)
    if host=='gaode':
        u='http://restapi.amap.com/v3/geocode/regeo?location='+p+'&extensions=base&output=json&key=d7307f1ea45bd1f25c3abba0f812e96d'
        r=urlopen(u).read()
        r=json.loads(r, encoding="utf-8")
        province=r['regeocode']['addressComponent']['province']
        city=r['regeocode']['addressComponent']['city']
        district=r['regeocode']['addressComponent']['district']
        township=r['regeocode']['addressComponent']['township']
        r=[i.encode('utf-8') if i else '' for i in [province,city,district,township]]
        r= ','.join(r)
    if host=='baidu':
        u='http://api.map.baidu.com/geocoder/v2/?ak=Mv6GpDpEey22Ir7BsbmRRxaT&callback=renderReverse&location='+p+'&output=json&pois=0'
        r=urlopen(u).read()
        r=json.loads(r[29:-1], encoding="utf-8")
        province=r['result']['addressComponent']['province']
        city=r['result']['addressComponent']['city']
        district=r['result']['addressComponent']['district']
        street=r['result']['addressComponent']['street']
        r=[i.encode('utf-8') if i else '' for i in [province,city,district,street]]
        r= ','.join(r)
    return r


def f2poi(host='gaode',f='apshift_9_12',fo='apshift_poi'):
    fh=open(f)
    fout=open(fo,'r')
    lout=fout.read().count('\n')
    fout.close()
    fout=open(fo,'a+')
    j=0
    for l in fh.readlines():
        j+=1
        if j<lout:
            continue
        if j % 10 == 0:
            print j
            time.sleep(6)
        if f=='apshift_9_12':
            l=l.strip().split(',')
            fout.write(l[0])
            lat1,lon1,lat2,lon2=l[1:]
        if f=='apshift_cnt1' or f=='apshift_cnt':
            l=l.split(';')
            fout.write(l[1].strip())
            lat1,lon1,lat2,lon2=l[0].split(',')
        if host=='gaode':
            p1=','.join([lat1,lon1])
            p2=','.join([lat2,lon2])
            r1=latlon2poi(p1,'gaode')
            r2=latlon2poi(p2,'gaode')
        if host=='baidu':
            p1=','.join([lon1,lat1])
            p2=','.join([lon2,lat2])
            r1=latlon2poi(p1,'baidu')
            r2=latlon2poi(p2,'baidu')
        fout.write(';')
        fout.write(r1)
        fout.write(';')
        fout.write(r2)
        fout.write('\n')
    fout.close()
    fh.close()

def shuffle_apshift():
    f=open('apshift_9_12')
    shift_dic={}
    for l in f.readlines():
        l=[i[:-2] for i in l.strip().split(',')[1:]]
        p=','.join(l)
        shift_dic[p]=shift_dic.get(p,0)+1
    out=sorted(shift_dic.items(),key=lambda k:k[1],reverse=True)
    fout=open('apshift_cnt1','w+')
    fout.write('\n'.join([';'.join(map(str,i)) for i in out]))
    fout.close()
    f.close()

def poiclust():
    f=open('apshift_9_12')
    poi_dic={}
    for l in f.readlines():
        l=[i[:-2] for i in l.strip().split(',')[1:]]
        p=','.join(l[:2])
        poi_dic[p]=poi_dic.get(p,0)+1
        p=','.join(l[2:])
        poi_dic[p]=poi_dic.get(p,0)+1
    print sorted(poi_dic.items(),key=lambda k:k[1],reverse=True)[:100]



if __name__ == "__main__":
    f2poi('baidu','apshift_cnt1','apshift_cnt1_poi')
    #poiclust()
