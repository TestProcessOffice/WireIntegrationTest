# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 13:18:40 2017

@author: COMAC
"""
from graphData import Neo4j
from models import FindFiles, Pgv, Jsw, Format, Save
from flask import Flask, render_template,url_for,request,redirect,flash

app = Flask("__name__")
db = Neo4j()

@app.route("/")
def root():
    return render_template("index.html")

@app.route("/graph_data",methods=['GET','POST'])
def graph_data():
    return render_template("graph_data.html")

@app.route("/jsw",methods=['POST'])
def jsw():
    res = request.form["jswfile"]
    print(res)
    jsw = Jsw(res)
    print("info_pv")
    print(jsw.info_pv)
    print("info_g")
    print(jsw.info_g)
    db.jsw_upload(jsw.info_pv,'pv')
    db.jsw_upload(jsw.info_g, 'g')
    flash("jsw file been uploaded")
    return render_template("graph_data.html")

@app.route("/ditmco",methods=['POST'])
def ditmco():
    res = request.form["ditmcofile"]
    print(res)
    pgv = Pgv(res)
    print("pgv_info:", pgv.info_lists)
    db.pgv_update(pgv.info_lists)
    flash("ditmco file been uploaded")
    return render_template("graph_data.html")


@app.route("/clear",methods=['POST'])
def clear():
    db.clear()
    flash("database been cleared")
    return render_template("graph_data.html")

@app.route("/piebar")
def piebar():
    data = db.stats()
    print(data)
    return render_template('piebar.html', data=data)

@app.route('/linebar')
def linebar():
    data = db.connector_status_dist()
    data = Format(data).jsons_DF()
    print(data)
    value, status, name = data[u'NUMBER'], data[u'STATUS'], data[u'CONNECTOR']
    value = [int(x) for x in value]
    name = [str(x) for x in name]
    #name = ['A-34N-P1', 'D-274D-P2', 'P-3316-P1', 'P-3316-P2', 'U-281-P2']
    data = {'NUMBER': value, 'CONNECTOR': name, 'STATUS':status}
    return render_template("linebar.html", data=data)

@app.route('/prog')
def prog():
    data1 = db.prog(label='insulation')
    data1 = Format(data1).jsons_DF()
    data2 = db.prog(label='continuity')
    data2 = Format(data2).jsons_DF()
    data = {'insulation': data1, 'continuity': data2}
    return render_template("prog.html", data)

@app.route("/highs")
def highs():
    data = db.prog(label='insulation|continuity')
    data = Format(data).jsons_DF()
    print(data)
    out = Save(data)
    out.to_html(path="./templates/highs.html")
    return render_template("highPin.html")


@app.route("/highhtml")
def highhtml():
    return render_template("highs.html")

@app.route("/prog/<something>")
def prog_database():
    return 'Execute operation: {0} '.format(something)


@app.route("/upload", methods=['POST'])
def upload():
    res=[]
    if request.method == "POST":
        res = request.form["jswfile"]
        print(res)
        jsw = Jsw(res)
        print(jsw.info_auto)
    return render_template('graph_data.html',res=res)