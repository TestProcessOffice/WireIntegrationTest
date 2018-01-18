# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import pandas as pd
import os
import re
"""
Created on Tue Dec 19 13:18:54 2017

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
        data_in = pd.read_excel(self._fin, sheet_name=Jsw.sheet_in[0])
        data_in = data_in.fillna('')
        data_in2 = pd.read_excel(self._fin, sheet_name=Jsw.sheet_in[1])
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
    columns = ["connector1", "pin1", "connector2", "pin2", "testType", "status", "value", "unit", "pin1_addr", "pin2_addr"]
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

class Format(object):
    def __init__(self, data):
        self._data = data

    def jsons_DF(self):
        self._data = pd.DataFrame(self._data)
        return self._data

    def continuty_test(self, df, start):
        row, col = df.shape
        data_out = pd.DataFrame(np.zeros((row * 2, 4)), dtype=str, columns=txt_out._col_name)
        for r_n in range(row):
            data_out.iloc[r_n * 2, 0:] = start, u'X-' + df.iloc[r_n, 0] + '-' + str(df.iloc[r_n, 1]), u'ATA-' + \
                                         df.iloc[r_n, 6].split('-')[0] + '-B1', u''
            data_out.iloc[r_n * 2 + 1, 0:] = u'', u'C-' + df.iloc[r_n, 3] + '-' + str(
                df.iloc[r_n, 4]), u'ATA-' + df.iloc[r_n, 6].split('-')[0] + '-B1', u''
            start += 1
        return data_out, start

    def _gnd_test(self, df, start):
        row, col = df.shape
        data_out = pd.DataFrame(np.zeros((row * 2, 4)), dtype=str, columns=txt_out._col_name)
        for r_n in range(row):
            data_out.iloc[r_n * 2, 0:] = start, u'X-' + df.iloc[r_n, 0] + '-' + str(df.iloc[r_n, 1]), u'ATA-' + \
                                         df.iloc[r_n, 6].split('-')[0] + '-B2', u''
            data_out.iloc[r_n * 2 + 1, 0:] = u'', u'C-' + df.iloc[r_n, 3], u'ATA-' + df.iloc[r_n, 6].split('-')[
                0] + '-B2', u''
            start += 1
        return data_out, start

    def save(self):
        with pd.ExcelWriter(self._fout) as writer:
            self.pd_out.to_excel(writer, sheet_name=self.sheet_out[0], index=False)
            self.pd_out2.to_excel(writer, sheet_name=self.sheet_out[1], index=False)
            self.pd_TB.to_excel(writer, sheet_name=self.sheet_out[2], index=False)

    def _ratio(self):
        '''
        calculate the ratio of HIGH result
        In -- {Node:(PASS number,HIGH number)}
        Return -- {Node: HIGH ratio}
        '''
        for key in self._stats:
            n_pass, n_high, _t = self._stats[key]
            self._stats[key] = n_pass, n_high, float(n_pass) / (n_pass + n_high)

    def _stats_sort(self, threshold=0.5):
        '''
        In -- {Connector: PASS Number,HIGH Number,PASS ratio,...}
        Return -- [(Node,ratio),...] with decrease order ,and > threshold
        '''
        lst = sorted(self._stats.items(), key=lambda d: sum(d[1]), reverse=True)
        lst = sorted(lst, key=lambda d: d[1][2], reverse=False)
        lst = filter(lambda d: d[1][2] > threshold, lst)
        return lst

    def _count(self):
        '''
        {'Connector Name':(PASS number,HIGH number,PASS ratio)}
        '''
        result = dict()
        row, col = self._lists.shape
        for i in range(row):
            info = self._lists.iloc[i]
            #            print(info)
            status, pin_a, pin_b = info[4], info[2], info[7]
            connector_a, connector_b = self._connector(pin_a), self._connector(pin_b)
            valueA = result.get(connector_a, (0, 0, 0))
            valueB = result.get(connector_b, (0, 0, 0))
            if status == 'PASS':
                result[connector_a] = (valueA[0] + 1, valueA[1], 0)
                result[connector_b] = (valueB[0] + 1, valueB[1], 0)
            elif status == 'HIGH':
                result[connector_a] = (valueA[0], valueA[1] + 1, 0)
                result[connector_b] = (valueB[0], valueB[1] + 1, 0)
        #        print(result)
        self._stats = result

    def analysis(self):
        '''
        '''
        self._lists_from_log()
        self._count()
        self._ratio()

    def prog_out(self, start=1):
        '''
        '''
        col_name = [u"No", u"测试程序", u"章节号", u"备注"]
        No, pins, chapter = [], [], []
        high_line = self._lists[self._lists["status"] == "HIGH"]
        row, col = high_line.shape
        for i in range(row):
            No.append(str(start + i))
            pins.append(high_line["pin_a"].iloc[i])
            chapter.append("")
            No.append("")
            pins.append(high_line["pin_b"].iloc[i])
            chapter.append("")
        pd_prog = pd.DataFrame([], columns=col_name)
        pd_prog[col_name[0]] = No
        pd_prog[col_name[1]] = pins
        pd_prog[col_name[2]] = chapter
        with pd.ExcelWriter(self._prog_out) as writer:
            pd_prog.to_excel(writer, sheet_name='retesting', index=False)

    def report_out(self, thr=0.5):
        '''
        Print out
        '''
        lst = self._stats_sort(threshold=thr)
        str_line = "===Node Name===PASS Ratio===\n"
        for item in lst:
            connector, passratio = item[0], item[1][2]
            str_line += "%12s%10.2f%%\n" % (connector, passratio * 100)

        with open(self._report_out, 'w') as fp:
            fp.write(str_line)


class Save(object):
    keys = (u'chapter', u'pin1', u'pin2')
    col_name = (u'No', u'测试程序', u'章节号', u'备注')

    def __init__(self, data):
        self.pdData = data
        pass

    def to_txt(self, path, fmt=None):
        column = self.pdData.columns
        n_row, n_col = self.pdData.shape
        header = ''
        for item in column:
            header += "{0:=^20}".format(item)
        header += "\n"
        lines = header
        for r in range(n_row):
            line = ''
            for item in self.pdData.iloc[r]:
                line += "{0:20}".format(item)
            line += '\n'
            lines += line
        with open(path, 'w') as fp:
            fp.write(lines)

    def to_csv(self, path, fmt=None):
        '''
        Print out
        '''
        self.pdData.to_csv(path, encoding='utf-8')

    def to_excel(self, path, sheet_name="sheet_1", fmt=None):
        self.pdData.to_excel(path, sheet_name=sheet_name, encoding='utf-8')

    def to_html(self, path, fmt=None):
        with open(path, 'wb') as fp:
            str_out = self.pdData.to_html()
            fp.write(str_out.encode('utf-8'))