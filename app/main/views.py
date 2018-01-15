# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 13:18:40 2017

@author: COMAC
"""
from graphData import Neo4j
from models import FindFiles, Pgv, Jsw, Format, Save
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

@app.route("/result")
def result():
    data = db.prog(label='insulation|continuity')
    data = Format(data).jsons_DF()
    print(data)
    out = Save(data)
    out.to_html(path="./templates/result.html")
    return render_template("highPin.html")

@app.route("/resulthtml")
def resulthtml():
    return render_template("result.html")

@app.route("/prog/<something>")
def prog_database():
    return 'Execute operation: {0} '.format(something)