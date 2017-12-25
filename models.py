# -*- coding: utf-8 -*-
import pandas as pd
import os
import re
"""
Created on Tue Dec 19 13:18:54 2017

@author: COMAC
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 14:43:49 2017

@author: COMAC
"""


class FindFiles(object):
    def __init__(self, folder_in = None, fileExt = '.txt'):
        self._rawfiles = []        
        try:
            for rt, dirs, files in os.walk(folder_in, topdown=False):
                for fl in files:
                    
                    fl = os.path.join(rt, fl)
                    fl = os.path.abspath(fl)
                    f = os.path.splitext(fl)
                    if f[1] == fileExt:
                        self._rawfiles.append(fl)

        except:
            print("Error Happen! ")

    def path(self):
        return self._rawfiles


class Jsw:
    '''
    info=[connector1,pin1,connector2,pin2,chapter,testType]
    '''
    columns = ['connector1','pin1','connector2','pin2','chapter','testType']
    type = ['continuity','insulation','tb']
    sheet_in = [u'连续性测试表', u'接地线导通测试表']
    sheet_out = [u'连续性测试程序', u'对地测试程序', u'TB']

    def __init__(self, fin):
        self._fin = fin
        self.info_auto, self.info_tb = None, None
        self._process()
        
    def _process(self):
        data_in = pd.read_excel(self._fin, sheetname=Jsw.sheet_in[0])
        data_in = data_in.fillna('')
        data_in2 = pd.read_excel(self._fin, sheetname=Jsw.sheet_in[1])
        data_in2 = data_in2.fillna('')
        data_in, data_tb = self.info_split(data_in)
        data_in2, data_tb2 = self.info_split(data_in2)
        data_in['testType'], data_tb['testType'] = Jsw.type[0], Jsw.type[2]
        data_in2['testType'], data_tb2['testType'] = Jsw.type[0], Jsw.type[2]
        self.info_auto = data_in.append(data_in2, ignore_index=True)
        self.info_auto.columns = Jsw.columns
        self.info_tb = data_tb.append(data_tb2, ignore_index=True)
        self.info_tb.columns = Jsw.columns
             
    def _hasTB(self, row_data):
        for data in row_data:
            if u"TB" in unicode(data):
                return True
        return False
    
    def _valid(self, row_data):
        cnt1 = row_data[0]
        cnt2 = row_data[3]
        mat1 = re.match("[\w-]+", unicode(cnt1))
        mat2 = re.match("[\w-]+", unicode(cnt2))
        
        if mat1 and mat2 and cnt1 == mat1.group() and cnt2 == mat2.group():
            return True
        return False
        
    def info_split(self,df):
        row, col = df.shape
        index_tb = []
        index_auto = [ ]
        column = [0, 1, 3, 4, 6]
        for r in range(row):
            if self._hasTB(df.iloc[r, :]):
                index_tb.append(r)
            elif self._valid(df.iloc[r, :]):
                index_auto.append(r)
                                
        info_tb = df.iloc[index_tb, column]
        info_auto = df.iloc[index_auto, column]
        return info_auto, info_tb


class Pgv:
    '''
    info=[connector1,pin1,connector2,pin2,chapter,\
    testType,status,value,unit,addr1,addr2]
    '''
    columns = ["connector1", "pin1", "connector2", "pin2", "testType", "status", "value", "unit", "pin1_addr", "pin1_addr"]
    typedic = {'FC': 'insulation', 'CC': 'continuity'}

    def __init__(self, file_in):
        '''
        '''
        self._file_in = file_in
        self.info_lists = None
        self._process()

    def _process(self):
        '''
        In -- TXT file of testing report
        Return -- [[ ],...]        
        '''
        fp = open(self._file_in, U'r')
        txt = fp.read()
        lists = []
        re1 = re.compile("(?<=:)\s+([A-Z]{2})\s+([0-9]+)\s+([0-9A-Z-]+)\s*:\s+([0-9]+)\s+([A-Z]+)\s+([0-9.M]+)\s+([A-Z]+)\s+([\w-]+)")
        for mat in re1.finditer(txt):
            line = mat.groups() #["command","addr1","pin1","addr2","status","value","unit","pin2"]
            pin1_addr, pin2_addr, status, value, unit = line[1], line[3], line[4], line[5], line[6]
            connector1, pin1 = self._connector_index(line[2])
            connector2, pin2 = self._connector_index(line[7])
            test_type = Pgv.typedic.get(line[0], 'NULL')
            line = [connector1, pin1, connector2, pin2, test_type, status, value, unit, pin1_addr, pin2_addr]
            lists.append(line)
        fp.close()
        self.info_lists = pd.DataFrame(lists, columns=Pgv.columns)
        
    def _connector_index(self, pin_name):
        '''
        In -- pin name
        Return -- Connector name
        '''
        re1 = re.compile("[0-9A-Z]+-*[0-9A-Z]*-*[0-9A-Z]*")
        mt = re1.search(pin_name)
        if mt:
            cnt = mt.group(0)
            return cnt, pin_name[len(cnt)+1:]
        else:
            return pin_name, ''