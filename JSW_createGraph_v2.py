# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 14:43:49 2017

@author: COMAC
"""
import pandas as pd
import numpy as np
import os
class jsw_files:
    def __init__(self,folder_in=None,filesub='-10102',folder_out = None):  
        sp = os.sep;
        self.rawfiles = []
        self.progfiles = []
        if folder_in is None:
            folder_in = "."+sp+"JSW_xls"
        if folder_out is None:
            folder_out = "."+sp+"prog"
        
        try:
            for rt,dirs,files in os.walk(folder_in,topdown=False):        
                for fl in files:
                    f = os.path.splitext(fl)
                    fl_n = f[0]+filesub+f[1]
                    self.rawfiles.append(os.path.join(rt,fl))
                    self.progfiles.append(os.path.join(folder_out,fl_n))
        except:
            print("Error Happen! ")
    

class jsw_xc:
    def __init__(self,fin,fout):
        self._fin,self._fout = fin,fout
        self.continuty,self._gnd,self._TB = None,None,None
        self.sheet_in = [u'连续性测试表',u'接地线导通测试表']
        self.sheet_out= [u'连续性测试程序',u'对地测试程序',u'TB']  
        
    def xc(self):
        start = 1
        data_in = pd.read_excel(self._fin,sheetname=self.sheet_in[0])
        data_in,data_TB =self._TB_split(data_in)
        self.pd_out,start = self._continuty_test(data_in,start)
            
        data_in2 = pd.read_excel(self._fin,sheetname=self.sheet_in[1])
        data_in2,data_TB2 =self._TB_split(data_in2)
        data_in2=data_in2.loc[1:,]
        self.pd_out2,start = self._gnd_test(data_in2,start)
        data_TB.append(data_TB2)
        self.pd_TB = data_TB
    
    def save(self):
        with pd.ExcelWriter(self._fout) as writer:
            self.pd_out.to_excel(writer,sheet_name=self.sheet_out[0],index=False)
            self.pd_out2.to_excel(writer,sheet_name=self.sheet_out[1],index=False)
            self.pd_TB.to_excel(writer,sheet_name=self.sheet_out[2],index=False)
             
    def _hasTB(self,row_data):
        for data in row_data:
            #print(data)
            if(u"TB" in unicode(data)): return True
        return False

    def _TB_split(self,df):
        row,col = df.shape
        index =[]
        for r in range(row):
            if(self._hasTB(df.iloc[r,:])): 
                index.append(r)
        df2 =df.iloc[index,:]
        df = df.drop(index)
        return df,df2
               
    def _continuty_test(self,df,start):
        row,col = df.shape
        col_name =[u'No',u'测试程序',u'章节号',u'备注']
        #col_df ={u"X-connector":0,u"X-pin":1,u"C-connector":3,u"C-pin":4,u"ATA":6}
        data_out = pd.DataFrame(np.zeros((row*2,4)),dtype=str,columns=col_name)
        for r_n in range(row):    
            data_out.iloc[r_n*2,0:]=start,u'X-'+df.iloc[r_n,0]+'-'+str(df.iloc[r_n,1]),u'ATA-'+df.iloc[r_n,6].split('-')[0]+'-B1',u''
            data_out.iloc[r_n*2+1,0:]=u'',u'C-'+df.iloc[r_n,3]+'-'+str(df.iloc[r_n,4]),u'ATA-'+df.iloc[r_n,6].split('-')[0]+'-B1',u''
            start +=1
        return data_out,start
    
    def _gnd_test(self,df,start):
        row,col = df.shape
        col_name =[u'No',u'测试程序',u'章节号',u'备注']
        #col_df ={u"X-connector":0,u"X-pin":1,u"C-connector":3,u"ATA":6}
        data_out = pd.DataFrame(np.zeros((row*2,4)),dtype=str,columns=col_name)    
        for r_n in range(row):    
            data_out.iloc[r_n*2,0:]=start,u'X-'+df.iloc[r_n,0]+'-'+str(df.iloc[r_n,1]),u'ATA-'+df.iloc[r_n,6].split('-')[0]+'-B2',u''
            data_out.iloc[r_n*2+1,0:]=u'',u'C-'+df.iloc[r_n,3],u'ATA-'+df.iloc[r_n,6].split('-')[0]+'-B2',u''
            start += 1
        return data_out,start


if __name__ =="__main__":    
    #strname = raw_input("Please input directory name of JSW files: ")
    files = jsw_files(folder_in="./JSW/JSW_xls",folder_out="./JSW/prog")
    jsw_files,prog_files = files.rawfiles,files.progfiles
    print(jsw_files)
    print(prog_files)
    for i in range(len(jsw_files)):
        jsw = jsw_xc(jsw_files[i],prog_files[i])
        jsw.xc()
        jsw.save()
                