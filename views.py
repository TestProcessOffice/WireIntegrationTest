# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 13:18:40 2017

@author: COMAC
"""
from dataBase import Neo4j
from models import FindFiles, Pgv, Jsw, Format, View
from flask import Flask, render_template, url_for

app = Flask("__name__")
db = Neo4j()

@app.route("/")
def root():
    return render_template("index.html")


@app.route("/jsw")
def jsw():
    return render_template("jsw.html")


@app.route("/dit_mco")
def dit_mco():
    return render_template("dit_mco.html")


@app.route("/piebar")
def piebar():
    data = db.stats()
    highvalue, passvalue=0,0
    for item in data:
        if item.get(u'name', 'NULL') == u'HIGH':
            highvalue = item.get(u'value')
        if item.get(u'name', 'NULL') == u'PASS':
            passvalue = item.get(u'value')
    data = passvalue, highvalue
    return render_template('piebar.html', data=data)


@app.route('/linebar')
def linebar():
    data = db.high_connector()
    fmt = Format(data)
    data = fmt.to_DF()
    value, name = data[u'value'],data[u'name']
    #value = [i for i in range(204)]
    value = [int(x) for x in value]
    name = [str(x) for x in name]
    #name = ['A-34N-P1', 'D-274D-P2', 'P-3316-P1', 'P-3316-P2', 'U-281-P2']
    data = value, name
    print(data)
    return render_template("linebar.html",data=data)

@app.route('/prog')
def prog():
    return render_template("prog.html")

@app.route("/result")
def result():
    data = db.prog()
    fmt = Format(data)
    data = fmt.to_DF()
    print(data)
    out = View(data)
    out.to_html(path="./templates/result.html")
    return render_template("result.html", data=data)



