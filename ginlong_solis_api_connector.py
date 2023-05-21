#!/usr/bin/python
"""Solis cloud API data fetcher."""
import base64
import datetime
import hashlib
import hmac
import json
import logging
import logging.config
import urllib
import urllib.parse
import time
import traceback
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request
import requests
import schedule
from influxdb import InfluxDBClient
from paho.mqtt import publish


def do_work():  # pylint: disable=too-many-locals disable=too-many-statements
    """worker loop"""

    # solis cloud api config
    api_key_id = ""  # os.environ['SOLIS_CLOUD_API_KEY_ID']
    api_key_pw = "".encode("utf-8")  # os.environ['SOLIS_CLOUD_API_KEY_SECRET'].encode("utf-8")
    domain = "https://www.soliscloud.com"  # os.environ['SOLIS_CLOUD_API_URL']
    port = "13333"  # os.environ['SOLIS_CLOUD_API_PORT']
    url = f'{domain}:{port}'
    # lan = os.environ['GINLONG_LANG']
    device_id = 0  # os.environ['SOLIS_CLOUD_API_INVERTER_ID']

    # == Constants ===============================================================
    http_function = "POST"
    mime_content_type = "application/json"
    endpoint_station_list = "/v1/api/userStationList"
    endpoint_inverter_list = "/v1/api/inverterList"
    endpoint_inverter_detail = "/v1/api/inverterDetail"
    endpoint_inverter_dayly = "/v1/api/inverterDay"
    endpoint_inverter_monthly = "/v1/api/inverterMonth"
    endpoint_inverter_yearly = "/v1/api/inverterYear"

    # == Output ==================================================================

    # Influx settings
    influx = ""  # os.environ['USE_INFLUX']
    influx_database = ""  # os.environ['INFLUX_DATABASE']
    influx_server = ""  # os.environ['INFLUX_SERVER']
    influx_port = ""  # os.environ['INFLUX_PORT']
    influx_user = ""  # os.environ['INFLUX_USER']
    influx_password = ""  # os.environ['INFLUX_PASSWORD']
    influx_measurement = ""  # os.environ['INFLUX_MEASUREMENT']

    # pvoutput
    pvoutput = ""  # os.environ['USE_PVOUTPUT']
    pvoutput_api = ""  # os.environ['PVOUTPUT_API_KEY']
    pvoutput_system = ""  # os.environ['PVOUTPUT_SYSTEM_ID']

    # MQTT
    mqtt = ""  # os.environ['USE_MQTT']
    mqtt_client = ""  # os.environ['MQTT_CLIENT_ID']
    mqtt_server = ""  # os.environ['MQTT_SERVER']
    mqtt_username = ""  # os.environ['MQTT_USERNAME']
    mqtt_password = ""  # os.environ['MQTT_PASSWORD']

    ###
    # == prettify json output ====================================================
    def prettify_json(input_json) -> str:
        """prettifies json for better output readability"""
        return json.dumps(json.loads(input_json), indent=2)

    # == post ====================================================================
    def execute_request(target_url, data, headers) -> str:
        """execute request and handle errors"""
        if data != "":
            post_data = data.encode("utf-8")
            request = Request(target_url, data=post_data, headers=headers)
        else:
            request = Request(target_url)
        error_string = ""
        try:
            with urlopen(request, timeout=30) as response:
                body = response.read()
                body_content = body.decode("utf-8")
                logging.debug("Decoded content: %s", body_content)
                return body_content
        except HTTPError as error:
            error_string = str(error.status) + ": " + error.reason
        except URLError as error:
            error_string = str(error.reason)
        except TimeoutError:
            error_string = "Request or socket timed out"
        except Exception as ex:  # pylint: disable=broad-except
            error_string = "urlopen exception: " + str(ex)
            traceback.print_exc()

        logging.error(target_url + " -> " + error_string)
        time.sleep(60)  # retry after 1 minute
        return "ERROR"

    # == get_solis_cloud_data ====================================================
    def get_solis_cloud_data(url_part, data) -> str:
        """get solis cloud data"""
        md5 = base64.b64encode(hashlib.md5(data.encode("utf-8")).digest()).decode("utf-8")
        while True:
            now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
            encrypt_str = (
                    http_function + "\n"
                    + md5 + "\n"
                    + mime_content_type + "\n"
                    + now + "\n"
                    + url_part
            )
            hmac_obj = hmac.new(
                api_key_pw,
                msg=encrypt_str.encode("utf-8"),
                digestmod=hashlib.sha1,
            )
            authorization = (
                    "API "
                    + api_key_id
                    + ":"
                    + base64.b64encode(hmac_obj.digest()).decode("utf-8")
            )
            headers = {
                "Content-MD5": md5,
                "Content-Type": mime_content_type,
                "Date": now,
                "Authorization": authorization,
            }
            data_content = execute_request(url + url_part, data, headers)
            logging.debug(url + url_part + "->" + prettify_json(data_content))
            if data_content != "ERROR":
                return data_content

    # == get_inverter_list_body ==================================================
    def get_inverter_list_body(time_category='', time_string='') -> str:
        """get inverter list body"""
        body = '{"userid":"' + api_key_id + '"}'
        data_content = get_solis_cloud_data(endpoint_station_list, body)
        station_info = json.loads(data_content)["data"]["page"]["records"][0]
        station_id = station_info["id"]

        body = '{"stationId":"' + station_id + '"}'
        data_content = get_solis_cloud_data(endpoint_inverter_list, body)
        inverter_info = json.loads(data_content)["data"]["page"]["records"][
            device_id
        ]
        inverter_id = inverter_info["id"]
        inverter_sn = inverter_info["sn"]

        if time_category== "":
            body = '{"id":"' + inverter_id + '","sn":"' + inverter_sn + '"}'
        else:
            body = '{"id":"' + inverter_id + '","sn":"' + inverter_sn + '","' + time_category + '":"' + time_string + '"}'
        logging.debug("body: %s", body)
        return body

    def get_inverter_details():
        inverter_detail_body = get_inverter_list_body()
        content = get_solis_cloud_data(endpoint_inverter_detail, inverter_detail_body)
        return json.loads(content)["data"]

    def get_inverter_day_data():
        inverter_detail_body = get_inverter_list_body()
        content = get_solis_cloud_data(endpoint_inverter_dayly, inverter_detail_body)
        return json.loads(content)["data"]


    def get_inverter_month_data():
        inverter_detail_body = get_inverter_list_body()
        content = get_solis_cloud_data(endpoint_inverter_monthly, inverter_detail_body)
        return json.loads(content)["data"]


    def get_inverter_year_data():
        inverter_detail_body = get_inverter_list_body()
        content = get_solis_cloud_data(endpoint_inverter_yearly, inverter_detail_body)
        return json.loads(content)["data"]

    def get_inverter_lastday_data():
        today = datetime.date.today()
        last_day = today - datetime.timedelta(days=1)
        str_last_day = last_day.strftime("%Y-%m-%d")
        inverter_detail_body = get_inverter_list_body('time',str_last_day)
        content = get_solis_cloud_data(endpoint_inverter_dayly, inverter_detail_body)
        return json.loads(content)["data"]
    def get_inverter_lastmonth_data():
        today = datetime.date.today()
        first = today.replace(day=1)
        lastMonth = first - datetime.timedelta(days=1)
        str_last_month = lastMonth.strftime("%Y-%m")
        inverter_detail_body = get_inverter_list_body('month',str_last_month)
        content = get_solis_cloud_data(endpoint_inverter_monthly, inverter_detail_body)
        return json.loads(content)["data"]

    def get_inverter_lastyear_data():
        today = datetime.date.today()
        first = today.replace(day=1,month=1)
        last_year = first - datetime.timedelta(days=1)
        str_last_year = last_year.strftime("%Y")
        inverter_detail_body = get_inverter_list_body('year',str_last_year)
        content = get_solis_cloud_data(endpoint_inverter_yearly, inverter_detail_body)
        return json.loads(content)["data"]


    # == MAIN ====================================================================
    def get_inverter_data():
        inverter_list_body = get_inverter_list_body()

        data_content = get_solis_cloud_data(endpoint_inverter_detail, inverter_list_body)
        inverter_detail_data = json.loads(data_content)["data"]

        return inverter_detail_data

    def write_to_influx_db(inverter_data, inverter_last_day, inverter_month, inverter_last_month, inverter_year, inverter_last_year, update_date):
        # Write to Influxdb
        if influx.lower() == "true":
            logging.info('InfluxDB output is enabled, posting outputs now...')

            #Building fields to export
            dict_detail=json.loads(inverter_data)
            dict_lastday=json.loads(inverter_data_last_day)
            dict_month=json.loads(inverter_month)
            dict_lastmonth=json.loads(inverter_data_lastmonth)
            dict_year=json.loads(inverter_year)
            dict_lastyear=json.loads(inverter_last_year)

            dict_fields={}
            dict_fields['DC_Voltage_PV1']           = dict_detail['uPv1']
            dict_fields['DC_Voltage_PV2']           = dict_detail['uPv2']
            dict_fields['DC_Voltage_PV3']           = dict_detail['uPv3']
            dict_fields['DC_Voltage_PV4']           = dict_detail['uPv4']
            dict_fields['DC_Current1']              = dict_detail['iPv1']
            dict_fields['DC_Current2']              = dict_detail['iPv2']
            dict_fields['DC_Current3']              = dict_detail['iPv3']
            dict_fields['DC_Current4']              = dict_detail['iPv4']
            dict_fields['AC_Voltage']               = (dict_detail['uAc1'] + dict_detail['uAc2'] + dict_detail['uAc3'])/3
            dict_fields['AC_Current']               = (dict_detail['iAc1'] + dict_detail['iAc2'] + dict_detail['iAc3'])/3
            dict_fields['AC_Power']                 = dict_detail['pac']
            dict_fields['AC_Frequency']             = dict_detail['fac']
            dict_fields['DC_Power_PV1']             = dict_detail['pow1']
            dict_fields['DC_Power_PV2']             = dict_detail['pow2']
            dict_fields['DC_Power_PV3']             = dict_detail['pow3']
            dict_fields['DC_Power_PV4']             = dict_detail['pow4']
            dict_fields['Inverter_Temperature']     = dict_detail['inverterTemperature']
            dict_fields['Daily_Generation']         = dict_detail['eToday']
            dict_fields['Monthly_Generation']       = dict_month['energy']
            dict_fields['Annual_Generation']        = dict_year['energy']
            dict_fields['Total_Generation']         = dict_detail['eTotal']
            dict_fields['Generation_Last_Month']    = dict_lastmonth['energy']
            dict_fields['Power_Grid_Total_Power']   = dict_detail['pSum']
            dict_fields['Total_On_grid_Generation'] = dict_detail['gridSellTotalEnergy']
            dict_fields['Total_Energy_Purchased']   = dict_detail['gridPurchasedTotalEnergy']
            dict_fields['Consumption_Power']        = dict_detail['familyLoadPower']
            dict_fields['Consumption_Energy']       = dict_detail['homeLoadTotalEnergy']
            dict_fields['Daily_Energy_Used']        = dict_detail['eToday'] - dict_detail['gridSellTodayEnergy']
            dict_fields['Monthly_Energy_Used']      = dict_month['energy'] - dict_month['gridSellEnergy']
            dict_fields['Annual_Energy_Used']       = dict_year['energy'] - dict_year['gridSellEnergy']
            dict_fields['Battery_Charge_Percent']   = ''

            #Read inverter_detail into dict
            dict_fields.update(dict_detail)

            inverter_json=json.dumps(dict_fields)

            json_body = [
                {
                    "measurement": influx_measurement,
                    "tags": {
                        "deviceId": device_id
                    },
                    "time": int(update_date),
                    "fields": inverter_json
                }
            ]

            logging.debug("sent to influxDb -> %s", prettify_json(json_body))

            if influx_user != "" and influx_password != "":
                client = InfluxDBClient(host=influx_server, port=influx_port, username=influx_user,
                                        password=influx_password)
            else:
                client = InfluxDBClient(host=influx_server, port=influx_port)

            client.switch_database(influx_database)
            success = client.write_points(json_body, time_precision='ms')
            if not success:
                logging.error('Error writing to influx database')

    def write_to_pvoutput(inverter_data, update_date):
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
            tuple_time = time.localtime(update_date / 1000)
            # Get hour and date
            date = time.strftime("%Y%m%d", tuple_time)
            hour = time.strftime("%H:%M", tuple_time)

            pvoutput_data = {
                "d": date,
                "t": hour,
                "v1": inverter_data['eToday'] * 1000,
                "v2": inverter_data['pac'],
                "v3": (inverter_data['eToday'] - inverter_data['gridSellTodayEnergy']) * 1000,
                "v4": inverter_data['familyLoadPower'],
                "v6": (inverter_data['uAc1'] + inverter_data['uAc2'] + inverter_data['uAc3']) / 3
            }
            # Python3 change
            encoded = urllib.parse.urlencode(pvoutput_data)

            pvoutput_result = requests.post(
                "http://pvoutput.org/service/r2/addstatus.jsp",
                data=encoded,
                headers=headers,
                timeout=120
            )
            logging.debug('PvOutput response: %s', pvoutput_result.content)
            if pvoutput_result.status_code != 200:
                logging.error('Error posting to PvOutput')

    def write_to_mqtt(inverter_data, update_date):
        # Push to MQTT
        if mqtt.lower() == "true":
            logging.info('MQTT output is enabled, posting results now...')

            msgs = []

            # Create the topic base using the client_id and serial number
            mqtt_topic = ''.join([mqtt_client, "/"])

            if mqtt_username != "" and mqtt_password != "":
                auth_settings = {'username': mqtt_username, 'password': mqtt_password}
            else:
                auth_settings = None

            msgs.append((mqtt_topic + "updateDate", int(update_date), 0, False))
            for key, value in inverter_data.items():
                msgs.append((mqtt_topic + key, value, 0, False))

            logging.debug("writing to MQTT -> %s", msgs)
            publish.multiple(msgs, hostname=mqtt_server, auth=auth_settings)

    if api_key_id == "" or api_key_pw == "":
        logging.error('Key ID and secret are mandatory for Solis Cloud API')
        return

    # download data
    inverter_detail = get_inverter_details()
    timestamp_current = inverter_detail["dataTimestamp"]
    inverter_data_last_day=get_inverter_lastday_data()
    inverter_data_month=get_inverter_month_data()
    inverter_data_lastmonth=get_inverter_lastmonth_data()
    inverter_data_year=get_inverter_year_data()
    inverter_data_lastyear=get_inverter_lastyear_data()

    # push to database
    json_formatted_str = json.dumps(inverter_detail, indent=2)
    logging.debug(json_formatted_str)

    # output data
    if influx == "true":
        write_to_influx_db(
            inverter_detail,
            inverter_data_last_day,
            inverter_data_month,
            inverter_data_lastmonth,
            inverter_data_year,
            inverter_data_lastyear,
            timestamp_current
        )

    if pvoutput == "true":
        write_to_pvoutput(inverter_detail, timestamp_current)

    if mqtt == "true":
        write_to_mqtt(inverter_detail, timestamp_current)


def main():
    """the main method"""

    global NEXT_RUN_YES  # pylint: disable=global-statement
    try:
        do_work()
    except Exception as exception:  # pylint: disable=broad-exception-caught
        logging.error('%s : %s', type(exception).__name__, str(exception))
    NEXT_RUN_YES = 1


global NEXT_RUN_YES  # pylint: disable=global-at-module-level

GET_LOGLEVEL = "debug"  # os.environ['LOG_LEVEL']
LOGLEVEL = logging.INFO
if GET_LOGLEVEL.lower() == "info":
    LOGLEVEL = logging.INFO
elif GET_LOGLEVEL.lower() == "error":
    LOGLEVEL = logging.ERROR
elif GET_LOGLEVEL.lower() == "debug":
    LOGLEVEL = logging.DEBUG

logging.basicConfig(level=LOGLEVEL, format='%(asctime)s %(levelname)s %(message)s')
logging.info('Started ginlong-solis-api-connector')

schedule.every(1).minutes.at(':00').do(main).run()
# schedule.every(5).minutes.at(':00').do(main).run()
while True:
    if NEXT_RUN_YES == 1:
        next_run = schedule.next_run().strftime('%d/%m/%Y %H:%M:%S')
        logging.info('Next run is scheduled at %s', next_run)
        NEXT_RUN_YES = 0
    schedule.run_pending()
    time.sleep(1)
