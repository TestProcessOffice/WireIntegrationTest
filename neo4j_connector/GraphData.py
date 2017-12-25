# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 10:40:53 2017

@author: COMAC
"""
from py2neo import Graph,Node,Relationship
class GraphData(object):
    def __init__(self):
        self._lables=["Pin","Continuity","Insulation"]
        self._graph = Graph()
    
    def create(self,info,jswtype):
        if jswtype == 'C':
            lable1,lable2 =self._lables[0],self._labels[1]
        elif jswtype == 'F':
            lable1,lable2 =self._lables[0],self._labels[2]
        try:
            i = 0
            for line in info:
                i += 1
                cntName1,pin1,cntName2,pin2,charpter = info
                fullName1,fullName2 = cntName1+'-'+pin1,cntName2+'-'+pin2
                node1 =Node(lable1,connectorName=cntName1,\
                        pinIndex=pin1,fullName=fullName1)
                node2 =Node(lable1,connectorName=cntName2,\
                        pinIndex=pin2,fullName=fullName2)        
                rel = Relationship(node1,lable2,node2,charpter=charpter,status='NULL',times=0,sequence= i)
                self._graph.create(rel)
        except:
            print("Error !")
        
    def update(self):
        pass
    
    def delete_all(self):
        pass
    
    def stats(self):
        pass
    