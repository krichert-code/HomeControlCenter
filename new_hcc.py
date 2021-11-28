#!/usr/bin/python

from flask import Flask, render_template, request, make_response, session, redirect, url_for
from flask_sessionstore import Session
import os
import json
import base64
import ConfigClass
import CryptClass
import APIClass
import HccDeamonClass
import ConnectorDeamonClass

app = Flask(__name__)



@app.route("/restApi", methods=['POST'])
def restApi():
    req = {}
    crypt = CryptClass.CryptClass()
    api = APIClass.APIClass()

    try:
        postData = crypt.DecodeWithId(request.data).decode()
        postData = postData[:postData.rfind("}")+1]
        req = json.loads( postData )
        response = api.invoke(req)
        return crypt.EncodeWithId(config.getHccId().encode("utf8"), response).decode()

    except Exception as e:
        print( "CRYPTO: wrong password")
        print (str(e))
        return ""



if (__name__ == "__main__"):
        config = ConfigClass.ConfigClass()
        config.initializeConfigData()

        hccDeamon = HccDeamonClass.HccDeamonClass()
        connectorDeamon = ConnectorDeamonClass.ConnectorDeamonClass()

        try:
            hccDeamon.start()
            #start connector deamon only if 'remote access' is enable (settings in configuration)
            connectorDeamon.start()

            app.run(host="0.0.0.0", port = 8090)
        except Exception as e:
            print( "Cannot run application ! Critical error")

        connectorDeamon.stop()
        hccDeamon.stop()
        hccDeamon.join()
        connectorDeamon.join()