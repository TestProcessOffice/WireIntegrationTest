# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 09:10:20 2017

@author: COMAC
"""
import pandas as pd
import numpy as np

class Format(object):
    def __init__(self,data):
        self._data = data
        
    def to_DF(self):
        self._data = pd.DataFrame(self._data)
        return self._data
    
    def continuty_test(self,df,start):
        row,col = df.shape
        data_out = pd.DataFrame(np.zeros((row*2,4)),dtype=str,columns=txt_out._col_name)
        for r_n in range(row):    
            data_out.iloc[r_n*2,0:]=start,u'X-'+df.iloc[r_n,0]+'-'+str(df.iloc[r_n,1]),u'ATA-'+df.iloc[r_n,6].split('-')[0]+'-B1',u''
            data_out.iloc[r_n*2+1,0:]=u'',u'C-'+df.iloc[r_n,3]+'-'+str(df.iloc[r_n,4]),u'ATA-'+df.iloc[r_n,6].split('-')[0]+'-B1',u''
            start +=1
        return data_out,start
    
    def _gnd_test(self,df,start):
        row,col = df.shape
        data_out = pd.DataFrame(np.zeros((row*2,4)),dtype=str,columns=txt_out._col_name)    
        for r_n in range(row):    
            data_out.iloc[r_n*2,0:]=start,u'X-'+df.iloc[r_n,0]+'-'+str(df.iloc[r_n,1]),u'ATA-'+df.iloc[r_n,6].split('-')[0]+'-B2',u''
            data_out.iloc[r_n*2+1,0:]=u'',u'C-'+df.iloc[r_n,3],u'ATA-'+df.iloc[r_n,6].split('-')[0]+'-B2',u''
            start += 1
        return data_out,start    

    def save(self):
        with pd.ExcelWriter(self._fout) as writer:
            self.pd_out.to_excel(writer,sheet_name=self.sheet_out[0],index=False)
            self.pd_out2.to_excel(writer,sheet_name=self.sheet_out[1],index=False)
            self.pd_TB.to_excel(writer,sheet_name=self.sheet_out[2],index=False)
    
    def _ratio(self):
        '''
        calculate the ratio of HIGH result
        In -- {Node:(PASS number,HIGH number)}
        Return -- {Node: HIGH ratio}
        '''
        for key in self._stats:
            n_pass,n_high,_t = self._stats[key]
            self._stats[key]= n_pass,n_high,float(n_pass)/(n_pass+n_high)  
                 
    def _stats_sort(self,threshold=0.5):
        '''
        In -- {Connector: PASS Number,HIGH Number,PASS ratio,...}
        Return -- [(Node,ratio),...] with decrease order ,and > threshold
        '''
        lst = sorted(self._stats.items(),key = lambda d:sum(d[1]),reverse=True)
        lst = sorted(lst,key = lambda d:d[1][2],reverse=False)
        lst = filter(lambda d:d[1][2]>threshold,lst)
        return lst      

    def _count(self):
        '''
        {'Connector Name':(PASS number,HIGH number,PASS ratio)}
        '''
        result = dict()
        row,col = self._lists.shape
        for i in range(row):
            info = self._lists.iloc[i]
#            print(info)
            status,pin_a,pin_b = info[4],info[2],info[7]
            connector_a ,connector_b = self._connector(pin_a),self._connector(pin_b)
            valueA = result.get(connector_a,(0,0,0))
            valueB = result.get(connector_b,(0,0,0))
            if status == 'PASS':
                result[connector_a] = (valueA[0]+1,valueA[1],0)
                result[connector_b] = (valueB[0]+1,valueB[1],0)
            elif status =='HIGH':
                result[connector_a] = (valueA[0],valueA[1]+1,0)
                result[connector_b] = (valueB[0],valueB[1]+1,0)
#        print(result)
        self._stats = result
        
         
    def analysis(self):   
        '''
        '''
        self._lists_from_log()
        self._count()
        self._ratio()
        
    def prog_out(self,start=1):
        '''        
        '''
        col_name=[u"No",u"测试程序",u"章节号",u"备注"]
        No,pins,chapter =[],[],[]
        high_line = self._lists[self._lists["status"]=="HIGH"]        
        row,col = high_line.shape
        for i in range(row):
            No.append(str(start+i))
            pins.append(high_line["pin_a"].iloc[i])
            chapter.append("")
            No.append("")
            pins.append(high_line["pin_b"].iloc[i])
            chapter.append("")
        pd_prog = pd.DataFrame([],columns=col_name)
        pd_prog[col_name[0]] = No
        pd_prog[col_name[1]] = pins
        pd_prog[col_name[2]] = chapter
        with pd.ExcelWriter(self._prog_out) as writer:
            pd_prog.to_excel(writer,sheet_name='retesting',index=False)
    
    def report_out(self,thr= 0.5):
        '''
        Print out
        '''
        lst=self._stats_sort(threshold=thr)          
        str_line = "===Node Name===PASS Ratio===\n" 
        for item in lst:
            connector,passratio = item[0],item[1][2]
            str_line += "%12s%10.2f%%\n"%(connector,passratio*100)
            
        with open(self._report_out,'w') as fp:    
            fp.write(str_line)