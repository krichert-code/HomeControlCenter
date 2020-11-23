import ConfigClass
import EventClass
import requests
import json
import os
import time
import copy
import socket
import fcntl
import struct
import sys
from datetime import date
from xml.dom import minidom


        
        
class AlarmClass(object):
    __port = "8081"
    __headers        = {'content-type': 'application/json'}
    __switch_req_state   = {"deviceid":"","data":{"switch":"on"}}
    __switch_req_info   = {"deviceid":"","data":{}}


    def __init__(self):
	pass
    
    def __get_ip(self, iface = 'eth0'):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sockfd = sock.fileno()
	SIOCGIFADDR = 0x8915

	ifreq = struct.pack('16sH14s', iface, socket.AF_INET, '\x00'*14)
	try:
	    res = fcntl.ioctl(sockfd, SIOCGIFADDR, ifreq)
	except:
	    return None
	ip = struct.unpack('16sH2x4s8x', res)[2]
	return socket.inet_ntoa(ip)

    def __get_netmask(self, iface = 'eth0'):
	netmask = socket.inet_ntoa(fcntl.ioctl(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), 35099, struct.pack('256s', iface))[20:24])
	return netmask


    def toggleSwitchState(self, ip):
	current_state = self.__getSwitchInfoForIp(ip)
	if current_state['error'] <> 0:
	    return current_state

	if current_state['data']['switch'] == "off":
	    state = "on"
	else:
	    state = "off"

	post_data = copy.deepcopy(SwitchClass.__switch_req_state)
	post_data['data']['switch'] = state
	req = "http://" + ip + ":" + self.__port + "/zeroconf/switch"
	output = requests.post(req, data=json.dumps(post_data), headers=SwitchClass.__headers, verify = False, timeout = 10)
	data = json.loads(output.text)
	response = {}
	response['error'] = data['error']
	response['switch'] = state
	return response

    def changeSwitchState(self, ip, state):
	post_data = copy.deepcopy(SwitchClass.__switch_req_state)
	post_data['data']['switch'] = state
	req = "http://" + ip + ":" + self.__port + "/zeroconf/switch"
	output = requests.post(req, data=json.dumps(post_data), headers=SwitchClass.__headers, verify = False, timeout = 10)
	data = json.loads(output.text)
	return data

    def getSwitchInfo(self, ip):
	return self.__getSwitchInfoForIp(ip)

    def __getSwitchInfoForIp(self,ip):
	post_data = copy.deepcopy(SwitchClass.__switch_req_info)
	req = "http://"+ip + ":" + self.__port + "/zeroconf/info"
	try:
	    output = requests.post(req, data=json.dumps(post_data), headers=SwitchClass.__headers, verify = False, timeout=(0.5, 10))
	    data = json.loads(output.text)
	except:
	    data = {}
	    data['error'] = 255
	return data

    def discoveryDevices(self):
	mask_byte_count = 0
	discovery = {}
	ip_addr_bytes = [255,255]
	ip = self.__get_ip()
	mask = self.__get_netmask()

	while (len(mask) > 0):
	    try:
		if (int(mask[mask.rindex(".") + 1:]) != 255):
		    mask_byte_count =  mask_byte_count + 1
		mask = mask[:mask.rindex(".")]
	    except:
		break

	ip_mask_bytes = 0
	while (mask_byte_count <> ip_mask_bytes):
	    ip = ip[:ip.rindex(".")]
	    ip_mask_bytes = ip_mask_bytes + 1

	for i in range(mask_byte_count):
	    ip_addr_bytes[i] = 0

	while(ip_addr_bytes[0] <> 255 or ip_addr_bytes[1] <> 255):
	    while(ip_addr_bytes[0] <> 255):
		try_ip = ip + "." + str(ip_addr_bytes[0])
		ip_addr_bytes[0] = ip_addr_bytes[0] + 1
		data = self.__getSwitchInfoForIp(try_ip)
		if (data['error'] == 0):
		    discovery[try_ip] = data['data']

	    if (ip_addr_bytes[1] <> 255):
		ip_addr_bytes[1] = ip_addr_bytes[1] +1
		ip_addr_bytes[0] = 0

	return discovery

    def getTemperature(self):
	config = ConfigClass.ConfigClass()
	alarm = config.getAlarmSystem()
	req = "http://" + alarm['ip'] + ":" + alarm['port'] + "/command=GetTemperature"
	try:
	    output = requests.get(req,  timeout=(0.5, 10))
	    xml = minidom.parseString(output.text)
	    data = {}
	    data['error'] = 0
	    elements = []
	    for item in xml.getElementsByTagName('sensors')[0].getElementsByTagName('sensor'):
		element = {}
		element['name'] = item.getElementsByTagName('sensorName')[0].firstChild.nodeValue
		element['value'] = item.getElementsByTagName('temperature')[0].firstChild.nodeValue
		element['thresholdExceeded'] = item.getElementsByTagName('thresholdExceeded')[0].firstChild.nodeValue
		elements.append(element)
	    data['temperature'] = elements
	except:
	    data = {}
	    data['error'] = 255
	return data

    def getAlerts(self):
	config = ConfigClass.ConfigClass()
	alarm = config.getAlarmSystem()
	req = "http://" + alarm['ip'] + ":" + alarm['port'] + "/command=GetAlerts"
	try:
	    output = requests.get(req,  timeout=(0.5, 10))
	    xml = minidom.parseString(output.text)
	    data = {}
	    data['error'] = 0
	    elements = []
	    for item in xml.getElementsByTagName('sensors')[0].getElementsByTagName('sensor'):
		element = {}
		element['name'] = item.getElementsByTagName('sensorName')[0].firstChild.nodeValue
		if (int(item.getElementsByTagName('alert')[0].firstChild.nodeValue) == 0):
		    element['alert'] = "off"
		else:
		    element['alert'] = "on"
		elements.append(element)
	    data['alerts'] = elements
	except:
	    data = {}
	    data['error'] = 255
	return data

    def getPresence(self):
	config = ConfigClass.ConfigClass()
	alarm = config.getAlarmSystem()
	req = "http://" + alarm['ip'] + ":" + alarm['port'] + "/command=GetPresence"
	try:
	    output = requests.get(req,  timeout=(0.5, 10))
	    xml = minidom.parseString(output.text)
	    data = {}
	    data['error'] = 0
	    elements = []
	    for item in xml.getElementsByTagName('sensors')[0].getElementsByTagName('sensor'):
		element = {}
		print "-------------" + item.getElementsByTagName('presenceState')[0].firstChild.nodeValue
		element['name'] = item.getElementsByTagName('sensorName')[0].firstChild.nodeValue
		if (int(item.getElementsByTagName('presenceState')[0].firstChild.nodeValue) == 0):
		    element['presence'] = 'off'
		else:
		    element['presence'] = 'on'
		elements.append(element)
	    data['presence'] = elements
	except:
	    data = {}
	    data['error'] = 255
	return data
