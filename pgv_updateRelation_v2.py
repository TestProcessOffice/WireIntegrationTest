# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 10:01:34 2017

@author: COMAC
"""
#import sys
import re
import pandas as pd
import os
class pgv_files:
    def __init__(self,folder_in=None,filesub='_sum',folder_out = None):  
        sp = os.sep;
        self.rawfiles = []
        self.progfiles = []
        self.statfiles = []
        if folder_in is None:
            folder_in = "."+sp+"Log"
        if folder_out is None:
            folder_out = "."+sp+"res"
        
        try:
            for rt,dirs,files in os.walk(folder_in,topdown=False):        
                for fl in files:
                    f = os.path.splitext(fl)
                    fl_prog = f[0]+filesub+".xlsx"
                    fl_stat = f[0]+filesub+".txt"
                    self.rawfiles.append(os.path.join(rt,fl))
                    self.progfiles.append(os.path.join(folder_out,fl_prog))
                    self.statfiles.append(os.path.join(folder_out,fl_stat))
        except:
            print("Error Happen! ")
    

class pgv:
    # line: command,addr_a,pin_a,addr_b,status,value,unit,pin_b
    def __init__(self,file_in,prog_out,report_out):
        '''
        '''
        self._file_in = file_in
        self._prog_out = prog_out
        self._report_out = report_out
        self._lists = pd.DataFrame([],columns=["command","addr_a","pin_a","addr_b","status","value","unit","pin_b"])
        self._stats = {} #{'Connector Name':(PASS number,HIGH number,PASS ratio)}

    def analysis(self):   
        '''
        '''
        self._lists_from_log()
        self._count()
        self._ratio()
        
    def prog_out(self,start=1):
        '''        
        '''
#        if (not self._lists):
#            print("No data found!")
#            return
        #print(self._lists)   
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
        print out
        '''
        lst=self._stats_sort(threshold=thr)          
        str_line = "===Node Name===PASS Ratio===\n" 
        for item in lst:
            connector,passratio = item[0],item[1][2]
            str_line += "%12s%10.2f%%\n"%(connector,passratio*100)
            
        with open(self._report_out,'w') as fp:    
            fp.write(str_line)
           
        
#    def _lists_from_log(self):
#        '''
#        In -- TXT file of testing report
#        Return -- [[ ],...]
#        '''
#        fp = open(self._file_in,U'r')
#        i = 0
#        lists =[]
#        for line in fp:
#            info = line.split()
#            if info and info[0]==':':
#                if i%2==0:
#                    lists.append(info[1:])
#                else:
#                    lists[i/2].extend(info[1:])
#                i += 1;
#        fp.close()
#        print(lists)
#        self._lists = pd.DataFrame(lists,columns=["command","addr_a","pin_a","addr_b","status","value","unit","pin_b"])   
    def _lists_from_log(self):
        '''
        In -- TXT file of testing report
        Return -- [[ ],...]
        '''
        fp = open(self._file_in,U'r')
        txt = fp.read()
        #i = 0
        lists =[]
        re1 =re.compile("(?<=:)\s+([A-Z]{2})\s+([0-9]+)\s+([0-9A-Z-]+)\s*:\s+([0-9]+)\s+([A-Z]+)\s+([0-9.M]+)\s+([A-Z]+)\s+([\w-]+)")
        for mat in re1.finditer(txt):
            line = mat.groups()
            lists.append(line)
        fp.close()
        #print(lists)
        self._lists = pd.DataFrame(lists,columns=["command","addr_a","pin_a","addr_b","status","value","unit","pin_b"])  
        
    def _connector(self,pin_name):
        '''
        In -- pin name
        Return -- Connector name
        '''
        re1 = re.compile("[0-9A-Z]+-[0-9A-Z]+-[0-9A-Z]+")
        mt = re1.search(pin_name)
        if mt:
            return mt.group(0)
        else:
            return pin_name    
     
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
       
#def show_out(lst):
#    import matplotlib.pyplot as plt
#    import numpy as np    
#
#    Node = map(lambda b:b[0],lst)
#    Ratio = map(lambda b:b[1],lst)
#    y_pos = np.arange(len(Node))
#    
#    plt.rcdefaults()
#    plt.rcParams.update({'figure.autolayout':True})
#    fig,ax = plt.subplots(figsize=(5,len(Node)))     
#    ax.barh(y_pos,Ratio,align='center',color='red')
#    ax.set_yticks(y_pos)
#    ax.set_yticklabels(Node)
#    ax.invert_yaxis()
#    ax.set_xlabel("HIGH Ratio")
#    ax.set_title("Cable Analysis Result")
#    plt.show()
    
    
#================================================
#======================================================    
if __name__=="__main__":
    "get report_file & analysis_file "
    log_file = "./pgv/log/gnd.txt"
    report_file ="./pgv/res/gnd_sum.txt"
    prog_file ="./pgv/res/gnd.xlsx"  
    print(prog_file)
    pgv1 = pgv(log_file,prog_file,report_file)
    pgv1.analysis()
    pgv1.report_out(thr=0.1)
    pgv1.prog_out()

