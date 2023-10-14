#!/usr/bin/python
# -*- coding: utf-8 -*-
import threading
import requests
import ConfigClass
import APIClass
import CryptClass
import json
import base64
import logging
import time
# ------------------------------------------------------------------------------------------------------------------------

class ConnectorDeamonClass(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

        config = ConfigClass.ConfigClass()
        self.__url = config.getHccServer().encode('utf-8')
        self.__id = config.getHccId().encode('utf-8')
        self.__stopEvent = False

    def stop(self):
        self.__stopEvent = True

    def run(self):
        log = logging.getLogger('werkzeug')
        logging.info('HCC connector start')

        apiObj = APIClass.APIClass()
        crypt = CryptClass.CryptClass()
        headers = {'Content-type': 'application/json',
                   'Accept': 'text/plain'}

        reg_data = {'action': 'registration' , 'type': 0 , 'data':''}
        response_data=""

        while not self.__stopEvent:
            try:
                reg_data['data'] = crypt.EncodeWithId(self.__id, response_data).decode()

                req = json.dumps(reg_data)

                response = requests.post(self.__url,
                        data=req,
                        headers=headers, timeout=None)

                if (len(response.text) == 0):
                    reg_data['type'] = 0
                    time.sleep(2)
                else:
                    postData = crypt.DecodeWithId(response.text.encode()).decode()
                    postData = postData[:postData.rfind('}') + 1]
                    logging.error("-------------get request " + postData)
                    response_data = apiObj.invoke(json.loads(postData))
                    logging.error("-------------get reponse " + response_data)
                    reg_data['type'] = 1
            except Exception as e:
                reg_data['type'] = 0
                logging.error('Connector exception : ' + str(e))
                time.sleep(5)