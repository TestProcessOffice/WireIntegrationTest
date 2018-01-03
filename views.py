# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 13:18:40 2017

@author: COMAC
"""
from dataBase import Neo4j
from models import FindFiles, Pgv, Jsw, Format, View
from flask import Flask, render_template, url_for

app = Flask("__name__")


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
    return render_template('piebar.html')


@app.route('/linebar')
def linebar():
    return render_template("linebar.html")

@app.route('/prog')
def prog():
    return render_template("prog.html")

@app.route("/result")
def result():
    db = Neo4j()
    data = db.prog()
    fmt = Format(data)
    data = fmt.to_DF()
    print(data)
    out = View(data)
    out.to_html(path="./templates/result.html")
    return render_template("result.html", data=data)



