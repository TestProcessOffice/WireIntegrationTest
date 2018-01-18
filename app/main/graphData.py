# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 10:40:53 2017
@author: jayHan

Modified 2018.1.4,15:44pm
function demonstration

"""
from py2neo import Graph,Node,Relationship
import numpy as np
import pandas as pd

class Neo4j(object):
    try:
        _graph = Graph()
    except:
        print("Please check database Neo4j!")
        exit(-1);

    _lables=["pin","continuity","insulation"]
    _jsw_columns = [u'connector1', u'pin1', u'connector2', u'pin2', u'chapter',u'testType']
    _pgv_columns = [u'connector1',u'pin1',u'connector2',u'pin2',u'testType',u'status',u'value',u'unit',u'addr1',u'addr2']
    def jsw_upload(self,info):
        '''
        upload new node and relationship to data base
        :param info: DataFrame with column name = _jsw_columns
        :return: True/False
        '''
        col = info.columns
        if not reduce(lambda x,y:x and y,col==Neo4j._jsw_columns):
            print("improper data format, please check!")
            return False
        try:
            #self.clear()
            print("to be")
            #set constraint
        except:
            print("Please check connection of Neo4j Database!")
            return False
        row,col = info.shape
        for r in range(row):
            print(info.iloc[r])
            cntName1,pin1,cntName2,pin2,chapter,testType = info.iloc[r]
            lable1,lable2 = "pin",testType
            if pin1 is np.nan or not pin1:
               fullName1 = unicode(cntName1)
            else:
               fullName1 = unicode(cntName1)+'-'+unicode(pin1)
            if pin2 is np.nan or not pin2:
               fullName2 = unicode(cntName2)
            else:
               fullName2 = unicode(cntName2)+'-'+unicode(pin2)
            node1 =Node(lable1,connectorName=cntName1,pinIndex=pin1,fullName=fullName1)
            node2 =Node(lable1,connectorName=cntName2,pinIndex=pin2,fullName=fullName2)
            rel = Relationship(node1, lable2, node2, chapter=chapter, status='NULL',times=0,sequence= r)

            Neo4j._graph.merge(rel)
        return True   
        
    def pgv_upload(self,info):
        '''
        modify property of existing relationship, or upload new node and relationship
        :param info:DataFrame with column name = _pvg_columns
        :return:False/True
        '''
        col = info.columns
        if not reduce(lambda x,y:x and y,col==Neo4j._pgv_columns):
            print("improper data format, please check!")
            return False
        try:
    #       ping database?
            print("to be ")
        except:
            print("Please check connection of Neo4j Database!")
            return False
        row,col = info.shape
        for r in range(row):
            cntName1,pin1,cntName2,pin2,testType,status,val,unit,addr1,addr2 = info.iloc[r]
            if pin1 is np.nan or not pin1:
               fullName1 = unicode(cntName1)
            else:
               fullName1 = unicode(cntName1)+'-'+unicode(pin1)
            if pin2 is np.nan or not pin2:
               fullName2 = unicode(cntName2)
            else:
               fullName2 = unicode(cntName2)+'-'+unicode(pin2)

            s1='''
            MERGE (node1:pin {fullName:{name1}})
            ON CREATE set node1.connectorName={cnt1},node1.pinIndex={pin1},node1.addr={addr1}
            ON MATCH set node1.addr = {addr1}
            MERGE (node2:pin {fullName:{name2}})
            On CREATE set node2.connectorName={cnt2},node1.pinIndex={pin2},node1.addr={addr2}
            ON MATCH set node2.addr = {addr2}
            '''
            s2='''
            MERGE (node1)-[rel:{testType}]->(node2)
            '''
            s3='''
            ON CREATE SET rel.times=0,rel.status={status},rel.value={value},rel.unit ={unit}
            WITH rel,rel.times as t
            SET rel.times = t+1,rel.status={status},rel.value={value},rel.unit ={unit}
            '''
            s2 = s2.format(testType=testType)
            query =s1+s2+s3
            
            Neo4j._graph.run(query,testType=testType,cnt1=cntName1,pin1=pin1,name1=fullName1,\
                             cnt2=cntName2,pin2=pin2,name2=fullName2,\
                             status=status,value=val,unit=unit,addr1=addr1,addr2=addr2)
        return True
    

    def pgv_update(self,info):
        '''
        Only modify property of existing relationship
        :param info:DataFrame with column name = _pvg_columns
        :return:False/True
        '''
        col = info.columns
        colName=["connector1","pin1","connector2","pin2","testType","status","value","unit","pin1_addr","pin2_addr"]
        if not reduce(lambda x,y:x and y,col==colName):
            print("improper data format, please check!")
            return False
        try:
    #       ping database?
            print("to be ")
        except:
            print("Please check connection of Neo4j Database!")
            return False
        row,col = info.shape
        for r in range(row):
            cntName1,pin1,cntName2,pin2,testType,status,val,unit,addr1,addr2 = info.iloc[r]
            if pin1 is np.nan or not pin1:
               fullName1 = unicode(cntName1)
            else:
               fullName1 = unicode(cntName1)+'-'+unicode(pin1)
            if pin2 is np.nan or not pin2:
               fullName2 = unicode(cntName2)
            else:
               fullName2 = unicode(cntName2)+'-'+unicode(pin2)

            query='''
            MATCH (pin1:pin)-[rel]->(pin2:pin)
            WHERE pin1.fullName = {name1} and pin2.fullName = {name2}
            WITH rel,pin1,pin2,rel.times as t
            SET rel.times = t+1,rel.status = {status},rel.value = {value},rel.unit = {unit},pin1.addr= {addr1},pin2.addr = {addr2}
            RETURN pin1,rel,pin2
            '''
            data = Neo4j._graph.run(query,name1=fullName1,name2=fullName2,\
                                 status=status,value=val,unit=unit,addr1=addr1,addr2=addr2)
            print(fullName1,fullName2,status,val,unit,addr1,addr2)
            print(data)
        return True
    
    
    def clear(self):
        Neo4j._graph.delete_all()


    def stats(self):
        '''
        stats. total number of 'HIGH','PASS' and 'NULL' status of test relationship
        :return: {"HIGH":n,"PASS":m,"NULL":p}
        '''
        result = {"HIGH":0,"PASS":0,"NULL":0}
        query = '''
        match(n1)-[rel1:continuity|insulation]-(n2)
        where rel1.status='HIGH'
        return count(rel1) as NUMBER
        '''
        data1 = Neo4j._graph.run(query).data()
        print(data1)
        result["HIGH"] = data1[0]['NUMBER']
        query = '''
        match(n1)-[rel1:continuity|insulation]-(n2)
        where rel1.status='PASS'
        return count(rel1) as NUMBER
        '''
        data2 = Neo4j._graph.run(query).data()
        result["PASS"] = data2[0]['NUMBER']
        query = '''
        match(n1)-[rel1:continuity|insulation]-(n2)
        where rel1.status='NULL'
        return count(rel1) as NUMBER
        '''
        data3 = Neo4j._graph.run(query).data()
        result["NULL"] = data3[0]['NUMBER']
        return result

    def prog(self, label):
        '''
        :label: label type of relationship,eg. continuity,insulation
        :return: (json objects)
        '''
        query='''
        MATCH (pin1:pin)-[rel:{label}]->(pin2:pin)
        WHERE rel.status='HIGH'
        RETURN pin1.fullName AS PIN1,pin2.fullName AS PIN2,rel.chapter as CHAPTER
        ORDER BY rel.sequence
        '''
        query = query.format(label=label)
        data = Neo4j._graph.run(query).data()

        return data

    def connector_status_dist(self):
        '''

        :return: json objects
        '''
        query = '''
        MATCH (pin1:pin)-[rel]->(pin2:pin)
        WHERE rel.status='HIGH'
        WITH pin1.connectorName as cnm
        MATCH (pin3:pin)-[rel2]->(pin4:pin)
        WHERE pin3.connectorName = cnm
        RETURN count(rel2.status) as NUMBER,rel2.status as STATUS,cnm as CONNECTOR
        '''
        data = Neo4j._graph.run(query).data()
        if not data:
            data = [{'NUMBER':0, 'STATUS':'NULL', 'CONNECTOR':None}]

        return data