# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 12:47:47 2017

@author: COMAC
"""
from main import app
import config
app.config.from_object(config)
app.run(host='0.0.0.0')

