# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 10:40:53 2017
@author: jayHan

Modified 2018.1.4,15:44pm
function demonstration

"""
from py2neo import Graph,Node,Relationship
import numpy as np

class Neo4j(object):
    try:
        _graph = Graph()
    except:
        print("Please check database Neo4j!")
        exit(-1);

    _lables=["pin","continuity","insulation"]
    _jsw_columns = [u'connector1', u'pin1', u'connector2', \
                        u'pin2', u'chapter',u'testType']
    _pgv_columns = ["connector1","pin1","connector2","pin2","testType","status","value","unit","addr1","addr2"] 
    def jsw_upload(self,info):
        col = info.columns
        if not reduce(lambda x,y:x and y,col==[u'connector1', u'pin1', u'connector2', \
                        u'pin2', u'chapter',u'testType']):
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
            node1 =Node(lable1,connectorName=cntName1,\
                    pinIndex=pin1,fullName=fullName1)
            node2 =Node(lable1,connectorName=cntName2,\
                    pinIndex=pin2,fullName=fullName2)        
            rel = Relationship(node1,lable2,node2,\
                    chapter=chapter,status='NULL',times=0,sequence= r)
            Neo4j._graph.merge(rel)
        return True   
        
    def pgv_upload(self,info):
        col = info.columns
        colName=["connector1","pin1","connector2","pin2","testType","status","value","unit","addr1","addr2"]
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
        col = info.columns
        colName=["connector1","pin1","connector2","pin2","testType","status","value","unit","addr1","addr2"]
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
            Neo4j._graph.run(query,name1=fullName1,name2=fullName2,\
                                 status=status,value=val,unit=unit,addr1=addr1,addr2=addr2)

        return True
    
    
    def clear(self):
        Neo4j._graph.delete_all()

    def high_connector(self):
        query ='''
        match (n1)-[rel1:continuity|insulation]-(n2)
        where rel1.status='HIGH'
        return count(rel1) as value,n1.connectorName as name 
        order by value desc    
        '''
        data3 = Neo4j._graph.run(query).data()
        return data3

    def new_prog(self,*args,**kwargs):
        query='''
        MATCH (pin1:pin)-[rel:{testType}]->(pin2:pin)
        WHERE rel.status='HIGH'
        RETURN pin1.fullName AS PIN1,pin2.fullName AS PIN2,rel.chapter as CHAPTER
        ORDER BY rel.sequence
        '''.format(*args,**kwargs)
        data = Neo4j._graph.run(query).data()
        return data

    def stats(self):
        query = '''
        match(n1)-[rel1:continuity|insulation]-(n2)
        where rel1.status='HIGH'
        return count(rel1) as value, rel1.status as name
        '''
        data1 = Neo4j._graph.run(query).data()
        query = '''
        match(n1)-[rel1:continuity|insulation]-(n2)
        where rel1.status='PASS'
        return count(rel1) as value,rel1.status as name
        '''
        data2 = Neo4j._graph.run(query).data()
        data1.extend(data2)
        return data1

    def prog(self):
        query='''
        MATCH (pin1:pin)-[rel]->(pin2:pin)
        WHERE rel.status='HIGH'
        RETURN pin1.fullName AS PIN1,pin2.fullName AS PIN2,rel.chapter as CHAPTER
        ORDER BY rel.sequence
        '''
        data = Neo4j._graph.run(query).data()
        return data

