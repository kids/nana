#encoding=utf-8

from ctypes import *


class tokenizer:
    
        def __init__(self):
            self._stext=['、','“','”','，','。','《','》','：','；','!','‘','’','?','？','！','·',' ',''] #枚举标点符号包括空格
            self._stopword_list=[line for line in file('D:\\prog\\ICTCLAS50\\Sample\\stopword.txt')]
            self._stopword_list=map(lambda x: x.strip(),self._stopword_list) # 去掉行尾的空格


        def parse(self,text):        
            atext_list=[]#存放要分词的文档
            rtext=[]#存放去标点符号和分词后的词
            participle = cdll.LoadLibrary('D:\\prog\\ICTCLAS50\\API\\ICTCLAS50.dll')
            participle.ICTCLAS_Init(c_char_p('D:\\prog\\ICTCLAS50\\API'))
            strlen = len(c_char_p(text).value)
            t = c_buffer(strlen*6)
            a =participle.ICTCLAS_ParagraphProcess(c_char_p(text),c_int(strlen),t,c_int(3),0)
            atext_list=t.value.split(' ')
            participle.ICTCLAS_Exit()
            rtext=[item for item in atext_list if item not in self._stext]
            result_list=[iword for iword in rtext if iword not in self._stopword_list]

            return result_list
			
text="文本的分类和聚类是一个比较有意思的话题，我以前也写过一篇blog《基于K-Means的文本聚类算法》，加上最近读了几本数据挖掘和机器学习的书籍，因此很想写点东西来记录下学习的所得。"
list=tokenizer().parse(text)

for item in list:
    print item
