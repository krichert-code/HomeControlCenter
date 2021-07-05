#!/usr/bin/python


import time
import CryptClass
import hashlib
from flask import Flask, render_template, request, make_response, session, redirect, url_for
from flask_sessionstore import Session
import threading

app = Flask(__name__)

t = {}
d = {}



@app.route("/register", methods=['POST'])
def register():    
    crypt = CryptClass.CryptClass()
    id = crypt.DecodeId(request.data)
    hash = hashlib.sha512(id).hexdigest()

    d[hash] = request.data

    if hash in t:
	#new response from HCC arrived
	t[hash].set()
    else:
	#first reuest from HCC (not response data)
	t[hash] = threading.Event()

    print "Wait for client request to ID = " +id+"(" + hash +")"
    t[hash].clear()
    t[hash].wait()
    return d[hash]


@app.route("/restApi", methods=['POST'])
def restApi():
    crypt = CryptClass.CryptClass()
    id = crypt.DecodeId(request.data)
    hash = hashlib.sha512(id).hexdigest()
    result = "device doesn't exist"

    if hash in t:
	d[hash] = request.data
	t[hash].set()
	print "Request from "+ id + " arrives"
	t[hash].clear()

	print "Waiting for data from HCC"
	t[hash].wait()
	result = d[hash]

    return result


if (__name__ == "__main__"):

	try:
	    app.run(host="0.0.0.0", port = 80)
	except Exception as e:
	    print "Cannot run application ! Critical error"

