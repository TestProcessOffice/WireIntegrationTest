# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 13:18:40 2017

@author: COMAC
"""
#import numpy as np
#import pandas as pd
#import itertools
#from template import *


class View(object):
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
