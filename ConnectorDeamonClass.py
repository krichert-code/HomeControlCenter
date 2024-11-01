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
from subprocess import Popen, PIPE
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

        command = ['ps -A -T | grep hcc.py']
        proc = Popen(
            command,
            shell=True,
            stdin=None,
            stdout=PIPE,
            stderr=None,
            close_fds=True,
            )

        logging.info('HCC connector pid')
        logging.info(str(proc.communicate()[0]))

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

                #logging.error("-------------Connector error code : registration")
                response = requests.post(self.__url,
                        data=req,
                        headers=headers, timeout=30)

                if (response.status_code != 200):
                    #logging.error("-------------Connector error code : " + str(response.status_code))
                    reg_data['type'] = 0
                    time.sleep(5)
                elif (len(response.text) == 0):
                    #logging.error("-------------Connector no request data available")
                    reg_data['type'] = 0
                    time.sleep(2)
                else:
                    postData = crypt.DecodeWithId(response.text.encode()).decode()
                    postData = postData[:postData.rfind('}') + 1]
                    #logging.error("-------------get request " + postData)
                    response_data = apiObj.invoke(json.loads(postData))
                    #logging.error("-------------get reponse " + response_data)
                    reg_data['type'] = 1

                response.close()

            except Exception as e:
                #logging.error('Connector exception : ' + str(e))
                response.close()
                reg_data['type'] = 0
                time.sleep(5)