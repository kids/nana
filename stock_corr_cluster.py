#coding=utf-8
import os
import numpy as np
import pandas as pd
import networkx as nx
from matplotlib import plot as plt

id_list = dict()
corr_list = []

def get_price(f):
	return np.loadtxt(f,delimiter=',',usecols=(1,),skiprows=1)

def get_id_list():
	for stock_file in os.listdir('.'):
		stock_id = stock_file.split('.')[0]
		if len(stock_id) == 6:# and int(stock_id)<10:
			print stock_id
			try:
				prices = get_price(stock_file)
				id_list[stock_id] = prices-np.average(prices)
			except:
				print 'error'

def calc(id1,id2):
	id1_prices = id_list[id1]
	id2_prices = id_list[id2]
	l = min(len(id1_prices),len(id2_prices))
	# err = id1_prices[:l] - id2_prices[:l]
	# err_relative = err
	# err_relative_abs = abs(err_relative)
	# err_relative_abs_avg = sum(err_relative_abs)/l
	vec1 = np.array(id1_prices[:l])
	vec2 = np.array(id2_prices[:l])
	return cosine_sim(vec1,vec2)

def norm1(nparr):
	return pow(sum(nparr**2),0.5)

def norm2(nparr):
	l = nparr.size
	return pow(l*sum(nparr**2)-sum(nparr)**2,0.5)

def cosine_sim(vec1,vec2):
	#inputs are np arrays
	numerator = sum(vec1*vec2)
	denominator = norm1(vec1)*norm1(vec2)
	#print numerator,denominator
	return abs(float(numerator)/denominator)

def cov(vec1,vec2):
	l = vec2.size
	return l*sum(vec1*vec2) - sum(vec1)*sum(vec2) 

def pearson_sim(vec1,vec2):
	l = vec2.size
	numerator = cov(vec1,vec2)
	denominator = norm2(vec1)*norm2(vec2)
	#print numerator,denominator
	return float(numerator)/denominator

def get_corr_list():
	get_id_list()
	key_list = id_list.keys()
	l = len(key_list)
	corr_list = np.zeros(pow(l,2))
	corr_list = corr_list.reshape(l,l)
	for i,key1 in enumerate(key_list):
		for j,key2 in enumerate(key_list):
			print i,j
			if i < j:
				corr_pair = calc(key1,key2)
				corr_list[i][j] = corr_pair
				corr_list[j][i] = corr_pair
	with open('corr_result.csv','w') as corr_result:
		corr_result.write(','.join(key_list))
		corr_result.write('\n')
		corr_result.write('\n'.join([','.join(map(str,x)) for x in corr_list]))



def get_corr(f='F:\\p\\qsmodel\\corr_result.csv'):
	curr_file = np.loadtxt(f,delimiter=',')
	id_index = curr_file[0]
	W = curr_file[1:]
	return id_index, W

def get_laplacian_matrix(W):
	d = [sum(row) for row in W]
	D = np.diag(d)
	L = D-W
	# symmetric norm
	Dn=np.power(np.linalg.matrix_power(D,-1),0.5)  
	L=np.dot(np.dot(Dn,L),Dn)  #np.diag(np.ones(len(d))) - ?
	return L

def getKSmallestEigVec(L,k):
	# return k smallest eigen values and their corresponding eigen vectors  
	eigval,eigvec=np.linalg.eig(L)
	dim=len(eigval)

	dictEigval=dict(zip(eigval,range(0,dim)))  
	kEig=np.sort(eigval)[0:k]  
	ix=[dictEigval[k] for k in kEig]  
	return eigval[ix],eigvec[:,ix]  
  
def checkResult(L,eigvec,eigval,k):  
	#print norm(L*eigvec[:,i]-lamda[i]*eigvec[:,i])   
	check=[np.dot(L,eigvec[:,i])-eigval[i]*eigvec[:,i] for i in range(0,k)]  
	length=[np.linalg.norm(e) for e in check]/np.spacing(1)  
	print("L*v-lamda*v are %s*%s" % (length,np.spacing(1)))  


def procedure():
	id_index, W = get_corr()
	L = get_laplacian_matrix(W)
	eigval,eigvec = getKSmallestEigVec(L, 20)
	r = np.hstack((id_index.reshape(-1,1),eigvec))
	with open('cluster20.csv','w+') as f:
		f.write('\n'.join([','.join(map(str,i)) for i in r])) 

def main():
	get_corr_list()
	procedure()

if __name__ == '__main__':
    main()
    
    
