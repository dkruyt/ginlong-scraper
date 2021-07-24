#!/usr/bin/python
import requests
import urllib
import json
import datetime
import time
import os
import logging
import schedule

# Not all keys are avilable depending on your setup
COLLECTED_DATA = {
    'DC_Voltage_PV1': '1a', 
    'DC_Voltage_PV2': '1b', 
	'DC_Voltage_PV3': '1c', 
	'DC_Voltage_PV4': '1d', 
    'DC_Current1': '1j', 
    'DC_Current2': '1k', 
	'DC_Current3': '1l', 
	'DC_Current4': '1m', 
    'AC_Voltage': '1ah', 
    'AC_Current': '1ak', 
    'AC_Power': '1ao', 
    'AC_Frequency': '1ar', 
    'DC_Power_PV1': '1s', 
    'DC_Power_PV2': '1t', 
    'DC_Power_PV3': '1u', 
    'DC_Power_PV4': '1v', 
    'Inverter_Temperature': '1df', 
    'Daily_Generation': '1bd', 
    'Monthly_Generation': '1be', 
    'Annual_Generation': '1bf', 
    'Total_Generation': '1bc', 
    'Generation_Last_Month': '1ru', 
    'Power_Grid_Total_Power': '1bq', 
    'Total_On_grid_Generation': '1bu', 
    'Total_Energy_Purchased': '1bv', 
    'Consumption_Power': '1cj', 
    'Consumption_Energy': '1cn', 
    'Daily_Energy_Used': '1co', 
    'Monthly_Energy_Used': '1cp', 
    'Annual_Energy_Used': '1cq', 
    'Battery_Charge_Percent': '1cv'
}

def do_work():
    # solis/ginlong portal config
    username        = os.environ['GINLONG_USERNAME']
    password        = os.environ['GINLONG_PASSWORD']
    domain          = os.environ['GINLONG_DOMAIN']
    lan             = os.environ['GINLONG_LANG']
    deviceId        = os.environ['GINLONG_DEVICE_ID']

    ### Output ###

    # Influx settings
    influx              = os.environ['USE_INFLUX']
    influx_database     = os.environ['INFLUX_DATABASE']
    influx_server       = os.environ['INFLUX_SERVER']
    influx_port         = os.environ['INFLUX_PORT']
    influx_user         = os.environ['INFLUX_USER']
    influx_password     = os.environ['INFLUX_PASSWORD']
    influx_measurement  = os.environ['INFLUX_MEASUREMENT']

    # pvoutput
    pvoutput            = os.environ['USE_PVOUTPUT']
    pvoutput_api        = os.environ['PVOUTPUT_API_KEY']
    pvoutput_system     = os.environ['PVOUTPUT_SYSTEM_ID']

    # MQTT
    mqtt                = os.environ['USE_MQTT']
    mqtt_client         = os.environ['MQTT_CLIENT_ID']
    mqtt_server         = os.environ['MQTT_SERVER']
    mqtt_username       = os.environ['MQTT_USERNAME']
    mqtt_password       = os.environ['MQTT_PASSWORD']

    ###

    if username == "" or password == "":
        logging.error('Username and password are mandatory for Ginlong Solis')
        return

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

    # login call
    loginSuccess = False
    try:
        resultData = session.post(url, data=params, headers=headers)
        resultJson = resultData.json()
        if resultJson.get('result') and resultJson.get('result').get('isAccept', 0) == 1:
            loginSuccess = True
            logging.info('Login successful for %s' % domain)
        else:
            raise Exception(json.dumps(resultJson))
    except Exception as e:
        logging.debug(e)
        logging.error('Login failed for %s' % domain)

    if loginSuccess:
        if deviceId == "":
            logging.info('Your deviceId is not set, auto detecting')
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
            logging.debug('Ginlong inverter list: %s' % json.dumps(resultJson))

            # .result.paginationAjax.data
            deviceId = resultJson['result']['paginationAjax']['data'][0]['deviceId']

            logging.info('Your deviceId is %s' % deviceId)

        # get device details
        url = 'http://'+domain+'/cpro/device/inverter/goDetailAjax.json'
        params = {
            'deviceId': int(deviceId)
        }

        cookies = {'language': lan}
        resultData = session.get(url, params=params, cookies=cookies, headers=headers)
        resultJson = resultData.json()
        logging.debug('Ginlong device details: %s' % json.dumps(resultJson))

        # Get values from json
        updateDate = resultJson['result']['deviceWapper'].get('updateDate')
        inverterData = {'updateDate': updateDate}
        for name,code in COLLECTED_DATA.items():
            inverterData[name] = float(0)
            value = resultJson['result']['deviceWapper']['dataJSON'].get(code)
            if value is not None:
                inverterData[name] = float(value)

        # Print collected values
        logging.debug('Results from %s:' % deviceId)
        logging.debug('%s' % time.ctime((updateDate) / 1000))
        for key,value in inverterData.items():
            logging.debug('%s: %s' % (key,value))

        # Write to Influxdb
        if influx.lower() == "true":
            logging.info('InfluxDB output is enabled, posting outputs now...')
            from influxdb import InfluxDBClient
            json_body = [
                {
                    "measurement": influx_measurement,
                    "tags": {
                        "deviceId": deviceId
                    },
                    "time": int(updateDate),
                    "fields": inverterData
                }
            ]
            if influx_user != "" and influx_password != "":
                client = InfluxDBClient(host=influx_server, port=influx_port, username=influx_user, password=influx_password )
            else:
                client = InfluxDBClient(host=influx_server, port=influx_port)
            
            client.switch_database(influx_database)
            success = client.write_points(json_body, time_precision='ms')
            if not success:
                logging.error('Error writing to influx database')

        # Write to PVOutput
        if pvoutput.lower() == "true":
            logging.info('PvOutput output is enabled, posting results now...')

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
                    "v1": inverterData['Daily_Generation'] * 1000,
                    "v2": inverterData['AC_Power'],
                    "v3": inverterData['Daily_Energy_Used'] * 1000,
                    "v4": inverterData['Consumption_Power'],
                    "v6": inverterData['AC_Voltage']
            }
#Python3 change
            encoded = urllib.parse.urlencode(pvoutputdata)

            pvoutput_result = requests.post("http://pvoutput.org/service/r2/addstatus.jsp", data=encoded, headers=headers)
            logging.debug('PvOutput response: %s' % pvoutput_result.content)
            if pvoutput_result.status_code != 200:
                logging.error('Error posting to PvOutput')

        # Push to MQTT
        if mqtt.lower() == "true":
            logging.info('MQTT output is enabled, posting results now...')

            import paho.mqtt.publish as publish
            msgs = []

            mqtt_topic = ''.join([mqtt_client, "/" ])   # Create the topic base using the client_id and serial number

            if (mqtt_username != "" and mqtt_password != ""):
                auth_settings = {'username':mqtt_username, 'password':mqtt_password}
            else:
                auth_settings = None
            
            msgs.append((mqtt_topic + "updateDate", int(updateDate), 0, False))
            for key,value in inverterData.items():
                msgs.append((mqtt_topic + key, value, 0, False))
            
            publish.multiple(msgs, hostname=mqtt_server, auth=auth_settings)


def main():
    global next_run_yes
    try:
        do_work()
    except Exception as e:
        logging.error('%s : %s' % (type(e).__name__, str(e)))
    next_run_yes = 1


global next_run_yes

get_loglevel = os.environ['LOG_LEVEL']
loglevel = logging.INFO
if get_loglevel.lower() == "info":
    loglevel = logging.INFO
elif get_loglevel.lower() == "error":
    loglevel = logging.ERROR
elif get_loglevel.lower() == "debug":
    loglevel = logging.DEBUG

logging.basicConfig(level=loglevel, format='%(asctime)s %(levelname)s %(message)s')
logging.info('Started ginlong-solis-scraper')

schedule.every(5).minutes.at(':00').do(main).run()
while True:
    if next_run_yes == 1:
        next_run = schedule.next_run().strftime('%d/%m/%Y %H:%M:%S')
        logging.info('Next run is scheduled at %s' % next_run)
        next_run_yes = 0
    schedule.run_pending()
    time.sleep(1)
