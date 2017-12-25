# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 12:47:47 2017

@author: COMAC
"""
from dataBase import Neo4j
from models import FindFiles,Pgv,Jsw
from views import View
from control import Format
print("Please confirm the name of directory:\n\
      JSW .xlsx files @ -'.\JSW\JSW_xls'\n\
      pgv .txt files  @ -'.\pgv\Log'\n")
raw_input("Ready?")

# link to database
db = Neo4j() 

## upload jsw info into database
#jsw_files = find_files(folder_in="./JSW/JSW_xls",fileExt='.xlsx').path()
#print(jsw_files)
#for i in range(len(jsw_files)):
#   jsw_1 = jsw(jsw_files[i])
#   auto = jsw_1.info_auto
#   tb = jsw_1.info_tb     
#   db.jsw_upload(auto)
#
## upload pgv info into database            
#log_files = find_files(folder_in="./pgv/Log",fileExt='.txt').path()
#print(log_files)
#for i in range(len(log_files)):
#   pgv_1 = pgv(log_files[i])
#   info = pgv_1.info_lists
#   db.pgv_upload(info)
#   #db.pgv_update(info)

# read info from database
data = db.prog()

#fmt ={{index},{u'pin1',u'pin2'},{u'chapter'}}
fmt = Format(data)
data = fmt.to_DF()
print(data)

out = View(data)
out.to_html(path="./pgv/result.html")

