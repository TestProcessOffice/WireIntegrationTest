# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 12:47:47 2017

@author: COMAC
"""
import JSW_processor as jp
import pgv_analyzer as pa
print("Please confirm the name of directory:\n\
      JSW .xlsx files @ -'.\JSW\JSW_xls'\n\
      prog folder exist -'.\JSW\prog'\n\
      pgv .txt files  @ -'.\pgv\Log'\n\
      out folder  exist -'.\pgv\out'")
raw_input("Ready?")

#strname = raw_input("Please input directory name of JSW files: ")
files1 = jp.jsw_files(folder_in=".\JSW\JSW_xls",folder_out=".\JSW\prog")
in_files,prog_files = files1.rawfiles,files1.progfiles
print("JSW processing:")
print(in_files,prog_files) 
for i in range(len(in_files)):
    jsw = jp.jsw_xc(in_files[i],prog_files[i])
    jsw.xc()
    jsw.save()
    
files2 = pa.pgv_files(folder_in=".\pgv\Log",folder_out=".\pgv\out")    
in_files,prog_files,stat_files = files2.rawfiles,files2.progfiles,files2.statfiles
print("\npgv processing:")
print(in_files,prog_files,stat_files)
for i in range(len(in_files)):
    pgv = pa.pgv(in_files[i],prog_files[i],stat_files[i])
    pgv.analysis()
    pgv.report_out(thr=0.0)
    pgv.prog_out()
raw_input("Ready to Quit!")    
