#!/usr/bin/python
import requests
import urllib
import json
import datetime
import time
import os
import logging
import schedule


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
        Power_Grid_Total_Power = resultJson['result']['deviceWapper']['dataJSON'].get('1bq')
        Total_On_grid_Generation = resultJson['result']['deviceWapper']['dataJSON'].get('1bu')
        if Generation_Last_Month is None:
            Generation_Last_Month = 0
        if Total_On_grid_Generation is None:
            Total_On_grid_Generation = 0
        Total_Energy_Purchased = resultJson['result']['deviceWapper']['dataJSON'].get('1bv')
        if Total_Energy_Purchased is None:
            Total_Energy_Purchased = 0
        Consumption_Power = resultJson['result']['deviceWapper']['dataJSON'].get('1cj')
        if Consumption_Power is None:
            Consumption_Power = 0
        Consumption_Energy = resultJson['result']['deviceWapper']['dataJSON'].get('1cn')
        if Consumption_Energy is None:
            Consumption_Energy = 0
        Daily_Energy_Used = resultJson['result']['deviceWapper']['dataJSON'].get('1co')
        if Daily_Energy_Used is None:
            Daily_Energy_Used = 0
        Monthly_Energy_Used = resultJson['result']['deviceWapper']['dataJSON'].get('1cp')
        if Monthly_Energy_Used is None:
            Monthly_Energy_Used = 0
        Annual_Energy_Used = resultJson['result']['deviceWapper']['dataJSON'].get('1cq')
        if Annual_Energy_Used is None:
            Annual_Energy_Used = 0
        Battery_Charge_Percent = resultJson['result']['deviceWapper']['dataJSON'].get('1cv')
        if Battery_Charge_Percent is None:
            Battery_Charge_Percent = 0
        niceTimestamp = time.ctime((updateDate) / 1000)

        # Print collected values
        logging.debug('Results from %d:')
        logging.debug('%s' % niceTimestamp)
        logging.debug('DC_Voltage_PV1: %s' % str(DC_Voltage_PV1))
        logging.debug('DC_Voltage_PV2: %s' % str(DC_Voltage_PV2))
        logging.debug('DC_Current1: %s' % str(DC_Current1))
        logging.debug('DC_Current2: %s' % str(DC_Current2))
        logging.debug('AC_Voltage: %s' % str(AC_Voltage))
        logging.debug('AC_Current: %s' % str(AC_Current))
        logging.debug('AC_Power: %s' % str(AC_Power))
        logging.debug('AC_Frequency: %s' % str(AC_Frequency))
        logging.debug('DC_Power_PV1: %s' % str(DC_Power_PV1))
        logging.debug('DC_Power_PV2: %s' % str(DC_Power_PV2))
        logging.debug('Inverter_Temperature: %s' % str(Inverter_Temperature))
        logging.debug('Daily_Generation: %s' % str(Daily_Generation))
        logging.debug('Monthly_Generation: %s' % str(Monthly_Generation))
        logging.debug('Annual_Generation: %s' % str(Annual_Generation))
        logging.debug('Total_Generation: %s' % str(Total_Generation))
        logging.debug('Generation_Last_Month: %s' % str(Generation_Last_Month))
        logging.debug('Power_Grid_Total_Power: %s' % str(Power_Grid_Total_Power))
        logging.debug('Total_On_grid_Generation: %s' % str(Total_On_grid_Generation))
        logging.debug('Total_Energy_Purchased: %s' % str(Total_Energy_Purchased))
        logging.debug('Consumption_Power: %s' % str(Consumption_Power))
        logging.debug('Consumption_Energy: %s' % str(Consumption_Power)) 
        logging.debug('Daily_Energy_Used: %s' % str(Daily_Energy_Used))
        logging.debug('Monthly_Energy_Used: %s' % str(Monthly_Energy_Used))
        logging.debug('Annual_Energy_Used: %s' % str(Annual_Energy_Used))
        logging.debug('Battery_Charge_Percent: %s' % str(Battery_Charge_Percent))


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
            "Power_Grid_Total_Power": float(Power_Grid_Total_Power),
            "Total_On_grid_Generation": float(Total_On_grid_Generation),
            "Total_Energy_Purchased": float(Total_Energy_Purchased),
            "Consumption_Power": float(Consumption_Power),
            "Consumption_Energy": float(Consumption_Energy),
            "Daily_Energy_Used": float(Daily_Energy_Used), 
            "Monthly_Energy_Used": float(Monthly_Energy_Used), 
            "Annual_Energy_Used": float(Annual_Energy_Used),
                    }
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
                    "v1": float(Daily_Generation) * 1000,
                    "v2": float(AC_Power),
                    "v3": float(Daily_Energy_Used) * 1000,
                    "v4": float(Consumption_Power),
                    "v6": float(AC_Voltage)
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
            msgs.append((mqtt_topic + "Power_Grid_Total_Power", float(Power_Grid_Total_Power), 0, False))
            msgs.append((mqtt_topic + "Total_On_grid_Generation", float(Total_On_grid_Generation), 0, False))
            msgs.append((mqtt_topic + "Total_Energy_Purchased", float(Total_Energy_Purchased), 0, False))
            msgs.append((mqtt_topic + "Consumption_Power", float(Consumption_Power), 0, False))
            msgs.append((mqtt_topic + "Consumption_Energy", float(Consumption_Energy), 0, False))
            msgs.append((mqtt_topic + "Daily_Energy_Used", float(Daily_Energy_Used), 0, False))
            msgs.append((mqtt_topic + "Monthly_Energy_Used", float(Monthly_Energy_Used), 0, False))
            msgs.append((mqtt_topic + "Annual_Energy_Used", float(Annual_Energy_Used), 0, False))
            msgs.append((mqtt_topic + "Battery_Charge_Percent", float(Battery_Charge_Percent), 0, False))
            
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
