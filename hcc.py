#!/usr/bin/python3


from flask import Flask, render_template, request, make_response, session, redirect, url_for
from flask_sessionstore import Session
import os
import time
import json
import base64
import ConfigClass
import CryptClass
import APIClass
import HccDeamonClass
import ConnectorDeamonClass
import AdminPanelSyncClass

app = Flask(__name__)
admiPanelSync = AdminPanelSyncClass.AdminPanelSyncClass()
api = APIClass.APIClass()

@app.route("/restApi", methods=['POST'])
def restApi():
    req = {}
    crypt = CryptClass.CryptClass()

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

@app.route("/", methods=['GET','POST'])
def adminPanel():
    config = ConfigClass.ConfigClass()
    if request.method == 'POST':
        config.updateConfiguration(request.form)
        admiPanelSync.notify()
        return "Success"
    else:
        return render_template('adminPanel.html', config=config)

if (__name__ == "__main__"):
        config = ConfigClass.ConfigClass()
        config.initializeConfigData()

        try:
            hccDeamon = HccDeamonClass.HccDeamonClass()
            admiPanelSync.registerObserver(hccDeamon)
            api.registerMedia(hccDeamon)
            hccDeamon.start()

            #sleep is only for get TID for logging purposes
            time.sleep(1)

            #start connector deamon only if 'remote access' is enable (settings in configuration)
            connectorDeamon = ConnectorDeamonClass.ConnectorDeamonClass()
            connectorDeamon.start()

            app.run(host="0.0.0.0", port = 80)
        except Exception as e:
            print( "Cannot run application ! Critical error")

        connectorDeamon.stop()
        hccDeamon.stop()
        hccDeamon.join()
        connectorDeamon.join()