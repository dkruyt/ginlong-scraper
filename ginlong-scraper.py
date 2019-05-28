#!/usr/bin/python
import requests
import urllib, urllib2
import json
import time

# solis/ginlong portal config
username		= 'user@name' #your portal username
password 		= 'password' #your portal password
domain 			= 'm.ginlong.com' #domain ginlong used multiple domains with same login but different versions, could change anytime. monitoring.csisolar.com, m.ginlong.com
lan 			= '2' #lanuage (2 = English)
deviceId        	= 'deviceid' # your deviceid, if set to deviceid it will try to auto detect, if you have more then one device then specify. 

### Output ###

# Influx settings
influx 			= 'true' # output result to influx set to false if you dont want to use
influx_database 	= 'dbname'
influx_server 		= 'localhost'
influx_port 		= '8086'
influx_measurement 	= 'PV'

# pvoutput
pvoutput 		= 'true' # output result to pvoutput set to false if you dont want to use
pvoutput_api 		= 'apikey'
pvoutput_system 	= 'pvsystem'

# MQTT
mqtt 			= 'true' # output result to mqtt set to false if you dont want to use
mqtt_client 		= 'pv'
mqtt_server 		= 'localhost'
mqtt_username 		= 'username'
mqtt_password 		= 'password'

###

# Create session for requests
session = requests.session()

# building url
url = 'https://'+domain+'/cpro/login/validateLogin.json'
params = {
    "userName": username,
    "password": password,
    "lan": lan,
    "domain": domain,
    "userType": "C"
}

# default heaeders gives a 403, seems releted to the request user agent, so we put curl here
headers = {'User-Agent': 'curl/7.58.0'}

#login call
resultData = session.post(url, data=params, headers=headers)

resultJson = resultData.json()
if resultJson['result'].get('isAccept') == 1:
    print "Login Succesfull on",domain,"!"
else:
    print "Login Failed on",domain,"!!"
    Exit()

if deviceId == "deviceid":
	print ''
	print "Your deviceId is not set, auto detecting"
	url = 'http://'+domain+'/cpro/epc/plantview/view/doPlantList.json'
	
	cookies = {'language': lan}
	resultData = session.get(url, cookies=cookies, headers=headers)
	resultJson = resultData.json()
	
	plantId = resultJson['result']['pagination']['data'][0]['plantId']

	url = 'http://'+domain+'/cpro/epc/plantDevice/inverterListAjax.json?'
	params = {
	    'plantId': int(plantId)
	}
	
	cookies = {'language': lan}
	resultData = session.get(url, params=params, cookies=cookies, headers=headers)
	resultJson = resultData.json()
	
	#.result.paginationAjax.data	
	deviceId = resultJson['result']['paginationAjax']['data'][0]['deviceId']
	
	print "Your deviceId is ",deviceId


# get device details
url = 'http://'+domain+'/cpro/device/inverter/goDetailAjax.json'
params = {
    'deviceId': int(deviceId)
}

cookies = {'language': lan}
resultData = session.get(url, params=params, cookies=cookies, headers=headers)
resultJson = resultData.json()

# Get values from json
updateDate = resultJson['result']['deviceWapper'].get('updateDate')
DC_Voltage_PV1 = resultJson['result']['deviceWapper']['dataJSON'].get('1a')
DC_Voltage_PV2 = resultJson['result']['deviceWapper']['dataJSON'].get('1b')
DC_Current1 = resultJson['result']['deviceWapper']['dataJSON'].get('1j')
DC_Current2 = resultJson['result']['deviceWapper']['dataJSON'].get('1k')
AC_Voltage = resultJson['result']['deviceWapper']['dataJSON'].get('1ah')
AC_Current = resultJson['result']['deviceWapper']['dataJSON'].get('1ak')
AC_Power = resultJson['result']['deviceWapper']['dataJSON'].get('1ao')
AC_Frequency = resultJson['result']['deviceWapper']['dataJSON'].get('1ar')
DC_Power_PV1 = resultJson['result']['deviceWapper']['dataJSON'].get('1s')
DC_Power_PV2 = resultJson['result']['deviceWapper']['dataJSON'].get('1t')
Inverter_Temperature = resultJson['result']['deviceWapper']['dataJSON'].get('1df')
Daily_Generation = resultJson['result']['deviceWapper']['dataJSON'].get('1bd')
Monthly_Generation = resultJson['result']['deviceWapper']['dataJSON'].get('1be')
Annual_Generation = resultJson['result']['deviceWapper']['dataJSON'].get('1bf')
Total_Generation = resultJson['result']['deviceWapper']['dataJSON'].get('1bc')
Generation_Last_Month = resultJson['result']['deviceWapper']['dataJSON'].get('1ru')

niceTimestamp = time.ctime((updateDate) / 1000)

# Print collected values
print "results from",domain
print('')
print niceTimestamp
print('')
print 'DC_Voltage_PV1: ' + str(DC_Voltage_PV1)
print 'DC_Voltage_PV2: ' + str(DC_Voltage_PV2)
print 'DC_Current1: ' + str(DC_Current1)
print 'DC_Current2: ' + str(DC_Current2)
print 'AC_Voltage: ' + str(AC_Voltage)
print 'AC_Current: ' + str(AC_Current)
print 'AC_Power: ' + str(AC_Power)
print 'AC_Frequency: ' + str(AC_Frequency)
print 'DC_Power_PV1: ' + str(DC_Power_PV1)
print 'DC_Power_PV2: ' + str(DC_Power_PV2)
print 'Inverter_Temperature: ' + str(Inverter_Temperature)
print "Daily_Generation: " + str(Daily_Generation)
print "Monthly_Generation: " + str(Monthly_Generation)
print "Annual_Generation: " + str(Annual_Generation)
print "Total_Generation: " + str(Total_Generation)
print "Generation_Last_Month: " + str(Generation_Last_Month)
print('')
print('')

# Write to Influxdb
if influx == "true":
	from influxdb import InfluxDBClient
	json_body = [
	    {
	        "measurement": influx_measurement,
	        "tags": {
	            "deviceId": deviceId
	        },
	        "time": int(updateDate),
	        "fields": {
	           	"DC_Voltage_PV1": float(DC_Voltage_PV1),
			"DC_Voltage_PV2": float(DC_Voltage_PV2),
			"DC_Current1": float(DC_Current1),
			"DC_Current2": float(DC_Current2),
			"AC_Voltage": float(AC_Voltage),
			"AC_Current": float(AC_Current),
			"AC_Power": float(AC_Power),
			"AC_Frequency": float(AC_Frequency),
			"Inverter_Temperature": float(Inverter_Temperature),
			"Daily_Generation": float(Daily_Generation),
			"Monthly_Generation": float(Monthly_Generation),
			"Annual_Generation": float(Annual_Generation),
			"updateDate": int(updateDate),
			"Total_Generation": float(Total_Generation),
			"Generation_Last_Month": float(Generation_Last_Month),
	        }
	   } 
	]
	
	client = InfluxDBClient(host=influx_server, port=influx_port)
	client.switch_database(influx_database)
	success = client.write_points(json_body, time_precision='ms')
	if not success:
	    print('error writing to influx database')

# Write to PVOutput
if pvoutput == "true":
	headers = {
	            "X-Pvoutput-Apikey": pvoutput_api,
	            "X-Pvoutput-SystemId": pvoutput_system,
	            "Content-type": "application/x-www-form-urlencoded",
	            "Accept": "text/plain"
	}
	
	# make seconds
	tuple_time = time.localtime(updateDate / 1000)
        # Get hour and date	
	date = time.strftime("%Y%m%d", tuple_time)
	hour = time.strftime("%H:%M", tuple_time)
	
	pvoutputdata = {
			"d": date,
			"t": hour,
			"v1": float(Daily_Generation) * 1000,
			"v2": float(AC_Power),
			"v5": float(Inverter_Temperature),
			"v6": float(AC_Voltage)
	}
	
	encoded = urllib.urlencode(pvoutputdata)
	
	pvoutput_result = requests.post("http://pvoutput.org/service/r2/addstatus.jsp", data=encoded, headers=headers)
	print "PVoutput: ",pvoutput_result.content


# Push to MQTT
if mqtt == "true":
        import paho.mqtt.publish as publish
	msgs = []
	
	mqtt_topic = ''.join([mqtt_client, "/" ])   # Create the topic base using the client_id and serial number
	
	msgs.append((mqtt_topic + "DC_Voltage_PV1", float(DC_Voltage_PV1), 0, False))
	msgs.append((mqtt_topic + "DC_Voltage_PV2", float(DC_Voltage_PV2), 0, False))
	msgs.append((mqtt_topic + "DC_Current1", float(DC_Current1), 0, False))
	msgs.append((mqtt_topic + "DC_Current2", float(DC_Current2), 0, False))
	msgs.append((mqtt_topic + "AC_Voltage", float(AC_Voltage), 0, False))
	msgs.append((mqtt_topic + "AC_Current", float(AC_Current), 0, False))
	msgs.append((mqtt_topic + "AC_Power", float(AC_Power), 0, False))
	msgs.append((mqtt_topic + "AC_Frequency", float(AC_Frequency), 0, False))
	msgs.append((mqtt_topic + "Inverter_Temperature", float(Inverter_Temperature), 0, False))
	msgs.append((mqtt_topic + "Daily_Generation", float(Daily_Generation), 0, False))
	msgs.append((mqtt_topic + "Monthly_Generation", float(Monthly_Generation), 0, False))
	msgs.append((mqtt_topic + "Annual_Generation", float(Annual_Generation), 0, False))
	msgs.append((mqtt_topic + "updateDate", int(updateDate), 0, False))
	msgs.append((mqtt_topic + "Total_Generation", float(Total_Generation), 0, False))
	msgs.append((mqtt_topic + "Generation_Last_Month", float(Generation_Last_Month), 0, False))
	
	publish.multiple(msgs, hostname=mqtt_server, auth={'username':mqtt_username, 'password':mqtt_password})

