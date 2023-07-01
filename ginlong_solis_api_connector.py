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
import os
from datetime import datetime, timezone, date
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request
import requests
import schedule
from influxdb import InfluxDBClient
from paho.mqtt import publish


def do_work():  # pylint: disable=too-many-locals disable=too-many-statements
    """worker loop"""

    # solis cloud api config
    api_key_id = os.environ['SOLIS_CLOUD_API_KEY_ID']
    api_key_pw = os.environ['SOLIS_CLOUD_API_KEY_SECRET'].encode("utf-8")
    domain = os.environ['SOLIS_CLOUD_API_URL']
    port = int(os.environ['SOLIS_CLOUD_API_PORT'])
    url = f'{domain}:{port}'
    device_id = int(os.environ['SOLIS_CLOUD_API_INVERTER_ID'])
    override_single_phase_inverter = os.environ['SOLIS_CLOUD_API_OVERRIDE_SINGLE_PHASE_INVERTER']
    api_retries = int(os.environ['SOLIS_CLOUD_API_NUMBER_RETRIES'])
    api_retries_timeout_s = int(os.environ['SOLIS_CLOUD_API_RETRIES_WAIT_S'])

    # == Constants ===============================================================
    http_function = "POST"
    mime_content_type = "application/json"
    endpoint_station_list = "/v1/api/userStationList"
    endpoint_inverter_list = "/v1/api/inverterList"
    endpoint_inverter_detail = "/v1/api/inverterDetail"
    endpoint_inverter_monthly = "/v1/api/inverterMonth"
    endpoint_inverter_yearly = "/v1/api/inverterYear"
    endpoint_inverter_all = "/v1/api/inverterAll"

    # == Output ==================================================================

    # Influx settings
    influx = os.environ['USE_INFLUX']
    influx_database = os.environ['INFLUX_DATABASE']
    influx_server = os.environ['INFLUX_SERVER']
    influx_port = int(os.environ['INFLUX_PORT'])
    influx_user = os.environ['INFLUX_USER']
    influx_password = os.environ['INFLUX_PASSWORD']
    influx_measurement = os.environ['INFLUX_MEASUREMENT']

    # pvoutput
    pvoutput = os.environ['USE_PVOUTPUT']
    pvoutput_api = os.environ['PVOUTPUT_API_KEY']
    pvoutput_system = os.environ['PVOUTPUT_SYSTEM_ID']
    pvex7 = os.environ['PVOUTPUT_EXTENDED_V7']
    pvex8 = os.environ['PVOUTPUT_EXTENDED_V8']
    pvex9 = os.environ['PVOUTPUT_EXTENDED_V9']
    pvex10 = os.environ['PVOUTPUT_EXTENDED_V10']
    pvex11 = os.environ['PVOUTPUT_EXTENDED_V11']
    pvex12 = os.environ['PVOUTPUT_EXTENDED_V12']

    # MQTT
    mqtt = os.environ['USE_MQTT']
    mqtt_client = os.environ['MQTT_CLIENT_ID']
    mqtt_server = os.environ['MQTT_SERVER']
    mqtt_topic_pfad = os.environ['MQTT_TOPIC']
    mqtt_port = int(os.environ['MQTT_PORT'])
    mqtt_username = os.environ['MQTT_USERNAME']
    mqtt_password = os.environ['MQTT_PASSWORD']

    ###
    # == prettify json output ====================================================
    def prettify_json(input_json) -> str:
        """prettifies json for better output readability"""
        return json.dumps(json.loads(input_json), indent=2)

    # == post ====================================================================
    def execute_request(target_url, data, headers, retries) -> str:
        """execute request and handle errors"""
        if data != "":
            post_data = data.encode("utf-8")
            request = Request(target_url, data=post_data, headers=headers)
        else:
            request = Request(target_url)
        try:
            with urlopen(request, timeout=30) as response:
                body = response.read()
                body_content = body.decode("utf-8")
                logging.debug("Decoded content: %s", body_content)
                return body_content
        except HTTPError as error:
            error_string = str(error.status) + ": " + error.reason

            if retries > 0:
                logging.warning(target_url + " -> " + error_string + " | retries left: " + retries )
                time.sleep(api_retries_timeout_s)
                execute_request(target_url, data, headers, retries - 1)
        except URLError as error:
            error_string = str(error.reason)
        except TimeoutError:
            error_string = "Request or socket timed out"
        except Exception as ex:  # pylint: disable=broad-except
            error_string = "urlopen exception: " + str(ex)
            traceback.print_exc()

        logging.error(target_url + " -> " + error_string)  # pylint: disable=used-before-assignment
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
            data_content = execute_request(url + url_part, data, headers, api_retries)
            logging.debug(url + url_part + " -> " + prettify_json(data_content))
            if data_content != "ERROR":
                return data_content

    # == get_inverter_list_body ==================================================
    def get_inverter_ids():
        body = '{"userid":"' + api_key_id + '"}'
        data_content = get_solis_cloud_data(endpoint_inverter_list, body)
        data_json = json.loads(data_content)["data"]["inverterStatusVo"]
        entries = data_json["all"]-1
        if device_id < 0:
            logging.error("'SOLIS_CLOUD_API_INVERTER_ID' has to be greater or equal to 0 " + \
                          "and lower than %s.", str(entries))
        if device_id > entries:
            logging.error("Your 'SOLIS_CLOUD_API_INVERTER_ID' (%s" + \
                          ") is larger than or equal to the available number of inverters (" + \
                          "%s). Please select a value between '0' and '%s'.", str(device_id),
                          str(entries), str(entries - 1))
        data_content = get_solis_cloud_data(endpoint_station_list, body)
        data_json = json.loads(data_content)["data"]["page"]["records"]
        station_info = data_json[device_id]
        station_id = station_info["id"]

        body = '{"stationId":"' + station_id + '"}'
        data_content = get_solis_cloud_data(endpoint_inverter_list, body)
        inverter_info = json.loads(data_content)["data"]["page"]["records"][device_id]
        return inverter_info["id"], inverter_info["sn"]

    def get_inverter_list_body(
            inverter_id_val,
            inverter_sn_val,
            time_category='',
            time_string=''
    ) -> str:
        if time_category == "":
            body = '{"id":"' + inverter_id_val + '","sn":"' + inverter_sn_val + '"}'
        else:
            body = '{"id":"' + inverter_id_val + \
                   '","sn":"' + inverter_sn_val + \
                   '","' + time_category + \
                   '":"' + time_string + '"}'
        logging.debug("body: %s", body)
        return body

    def get_inverter_details(inverter_id_val, inverter_sn_val):
        inverter_detail_body = get_inverter_list_body(inverter_id_val, inverter_sn_val)
        content = get_solis_cloud_data(endpoint_inverter_detail, inverter_detail_body)
        return json.loads(content)["data"]

    def get_inverter_month_data(inverter_id_val, inverter_sn_val):
        today = date.today()
        str_month = today.strftime("%Y-%m")
        inverter_detail_body = get_inverter_list_body(
            inverter_id_val,
            inverter_sn_val,
            'month',
            str_month
        )
        content = get_solis_cloud_data(endpoint_inverter_monthly, inverter_detail_body)
        return json.loads(content)["data"]

    def get_inverter_year_data(inverter_id_val, inverter_sn_val):
        today = date.today()
        str_year = today.strftime("%Y")
        inverter_detail_body = get_inverter_list_body(
            inverter_id_val,
            inverter_sn_val,
            'year',
            str_year
        )
        content = get_solis_cloud_data(endpoint_inverter_yearly, inverter_detail_body)
        return json.loads(content)["data"]

    def get_inverter_all_data(inverter_id_val, inverter_sn_val):
        inverter_detail_body = get_inverter_list_body(inverter_id_val, inverter_sn_val)
        content = get_solis_cloud_data(endpoint_inverter_all, inverter_detail_body)
        return json.loads(content)["data"]

    def get_ac_voltage(inverter_data):
        return get_average_value(inverter_data, 'uAc1', 'uAc2', 'uAc3')

    def get_ac_current(inverter_data):
        return get_average_value(inverter_data, 'iAc1', 'iAc2', 'iAc3')

    def get_average_value(inverter_data, field_phase_1, field_phase_2, field_phase_3):
        if int(inverter_data['acOutputType']) == 0 or override_single_phase_inverter == 'true':  # pylint: disable=line-too-long
            average_value = float(inverter_data[field_phase_1])
        else:
            average_value = float((inverter_data[field_phase_1] + inverter_data[field_phase_2] + inverter_data[field_phase_3]) / 3)  # pylint: disable=line-too-long
        return average_value

    def convert_dict_details_to_float(dict_to_change, parameters):
        for param in parameters:
            dict_to_change[param] = float(dict_to_change[param])
        return dict_to_change

    def get_last_month_generation(dict_year):
        generation_last_month = 0.0
        if len(dict_year) > 1:
            generation_last_month = float(dict_year[-2]['energy'])

        return generation_last_month


    # == MAIN ====================================================================
    # Write to Influxdb
    def write_to_influx_db(inverter_data, inverter_month, inverter_year, inverter_all, update_date):
        if influx.lower() == "true":
            logging.info('InfluxDB output is enabled, posting outputs now...')

            # Building fields to export
            dict_detail = inverter_data
            dict_month = inverter_month  # pylint: disable=unused-variable
            dict_year = inverter_year
            dict_all = inverter_all  # pylint: disable=unused-variable

            dict_fields = {'DC_Voltage_PV1': float(dict_detail['uPv1']),
                           'DC_Voltage_PV2': float(dict_detail['uPv2']),
                           'DC_Voltage_PV3': float(dict_detail['uPv3']),
                           'DC_Voltage_PV4': float(dict_detail['uPv4']),
                           'DC_Current1': float(dict_detail['iPv1']),
                           'DC_Current2': float(dict_detail['iPv2']),
                           'DC_Current3': float(dict_detail['iPv3']),
                           'DC_Current4': float(dict_detail['iPv4']),
                           'AC_Voltage': get_ac_voltage(dict_detail),
                           'AC_Current': get_ac_current(dict_detail),
                           'AC_Power': float(dict_detail['pac'] * 1000),
                           'AC_Frequency': float(dict_detail['fac']),
                           'DC_Power_PV1': float(dict_detail['pow1']),
                           'DC_Power_PV2': float(dict_detail['pow2']),
                           'DC_Power_PV3': float(dict_detail['pow3']),
                           'DC_Power_PV4': float(dict_detail['pow4']),
                           'Inverter_Temperature': float(dict_detail['inverterTemperature']),
                           'Daily_Generation': float(dict_detail['eToday']),
                           'Monthly_Generation': float(dict_detail['eMonth']),
                           'Annual_Generation': float(dict_detail['eYear']),
                           'Total_Generation': float(dict_detail['eTotal'] * 1000),
                           'Generation_Last_Month': get_last_month_generation(dict_year),
                           'Power_Grid_Total_Power': float(dict_detail['psum'] * 1000),
                           'Total_On_grid_Generation': float(dict_detail['gridSellTotalEnergy'] * 1000),  # pylint: disable=line-too-long
                           'Total_Energy_Purchased': float(dict_detail['gridPurchasedTotalEnergy'] * 1000),  # pylint: disable=line-too-long
                           'Consumption_Power': float(dict_detail['familyLoadPower'] * 1000),
                           'Consumption_Energy': float(dict_detail['homeLoadTotalEnergy'] * 1000),
                           'Daily_Energy_Used': float(dict_detail['eToday'] - dict_detail['gridSellTodayEnergy']),  # pylint: disable=line-too-long
                           'Monthly_Energy_Used': float(dict_detail['eMonth'] - dict_detail['gridSellMonthEnergy']),  # pylint: disable=line-too-long
                           'Annual_Energy_Used': float(dict_detail['eYear'] - dict_detail['gridSellYearEnergy']),  # pylint: disable=line-too-long
                           'updateDate': int(dict_detail['dataTimestamp'])
                           }

            # Read inverter_detail into dict
            changelist=["iPv1","iPv2","iPv3","iPv4","iPv5",
                        "iPv6","iPv7","iPv8","iPv9","iPv10",
                        "iPv11","iPv12","iPv13","iPv14","iPv15",
                        "iPv16","iPv17","iPv18","iPv19","iPv20",
                        "iPv21","iPv22","iPv23","iPv24","iPv25",
                        "iPv26","iPv27","iPv28","iPv29","iPv30",
                        "iPv31","iPv32",
                        "uPv1","uPv2","uPv3","uPv4","uPv5",
                        "uPv6","uPv7","uPv8","uPv9","uPv10",
                        "uPv11", "uPv12", "uPv13","uPv14", "uPv15",
                        "uPv16", "uPv17", "uPv18", "uPv19", "uPv20",
                        "uPv21", "uPv22", "uPv23", "uPv24","uPv25",
                        "uPv26", "uPv27", "uPv28", "uPv29","uPv30",
                        "uPv31", "uPv32",
                        "iAc1","iAc2","iAc3","uAc1","uAc2","uAc3"]
            dict_float = convert_dict_details_to_float(dict_detail,changelist)
            dict_fields.update(dict_float)

            influx_to_submit = [
                {
                    "measurement": influx_measurement,
                    "tags": {
                        "deviceId": device_id
                    },
                    "time": int(update_date),
                    "fields": dict_fields
                }
            ]

            if influx_user != "" and influx_password != "":
                client = InfluxDBClient(host=influx_server, port=influx_port, username=influx_user,
                                        password=influx_password)
            else:
                client = InfluxDBClient(host=influx_server, port=influx_port)

            client.switch_database(influx_database)
            success = client.write_points(influx_to_submit, time_precision='ms')
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
            tuple_time = time.localtime(int(update_date) / 1000)
            # Get hour and date
            pv_date = time.strftime("%Y%m%d", tuple_time)
            pv_hour = time.strftime("%H:%M", tuple_time)

            pvoutput_data = {
                # output date [yyyymmdd] as int
                "d": pv_date,
                # time [hh:mm]
                "t": pv_hour,
                # energy generation (int, Wh)
                "v1": inverter_data['eToday'] * 1000,
                # power generation (int, W)
                "v2": inverter_data['pac'] * 1000,
                # energy consumption (int, Wh)
                "v3": inverter_data['homeLoadTotalEnergy'] * 1000,
                # power consumption (int, W)
                "v4": inverter_data['familyLoadPower'] * 1000,
                # temperature (float, °C), not available by inverter data
                # "v5": 0.0,
                # voltage (float, V)
                "v6": get_ac_voltage(inverter_data)
            }

            if pvex7 != "":
                pvoutput_data["v7"] = inverter_data[pvex7]
            if pvex8 != "":
                pvoutput_data["v8"] = inverter_data[pvex8]
            if pvex9 != "":
                pvoutput_data["v9"] = inverter_data[pvex9]
            if pvex10 != "":
                pvoutput_data["v10"] = inverter_data[pvex10]
            if pvex11 != "":
                pvoutput_data["v11"] = inverter_data[pvex11]
            if pvex12 != "":
                pvoutput_data["v12"] = inverter_data[pvex12]

            # Python3 change
            encoded = urllib.parse.urlencode(pvoutput_data)

            pvoutput_result = requests.post(
                "https://pvoutput.org/service/r2/addstatus.jsp",
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

            # Topic base using the env mqtt_topic_pfad + client ID
            mqtt_topic = ''.join([mqtt_topic_pfad, "/", mqtt_client, "/"])

            if mqtt_username != "" and mqtt_password != "":
                auth_settings = {'username': mqtt_username, 'password': mqtt_password}
            else:
                auth_settings = None

            msgs.append((mqtt_topic + "updateDate", int(update_date), 0, False))
            for key, value in inverter_data.items():
                msgs.append((mqtt_topic + key, value, 0, False))

            logging.debug("writing to MQTT -> %s", msgs)
            publish.multiple(msgs, hostname=mqtt_server, port=mqtt_port, client_id=mqtt_client, auth=auth_settings)  # pylint: disable=line-too-long

    if api_key_id == "" or api_key_pw == "":
        logging.error('Key ID and secret are mandatory for Solis Cloud API')
        return

    # download data
    inverter_result = get_inverter_ids()
    inverter_id = inverter_result[0]
    inverter_sn = inverter_result[1]
    inverter_detail = get_inverter_details(inverter_id, inverter_sn)
    timestamp_current = inverter_detail["dataTimestamp"]
    inverter_data_month = get_inverter_month_data(inverter_id, inverter_sn)
    inverter_data_year = get_inverter_year_data(inverter_id, inverter_sn)
    inverter_data_all = get_inverter_all_data(inverter_id, inverter_sn)

    # push to database
    json_formatted_str = json.dumps(inverter_detail, indent=2)
    logging.debug(json_formatted_str)

    # output data
    if influx == "true":
        write_to_influx_db(
            inverter_detail,
            inverter_data_month,
            inverter_data_year,
            inverter_data_all,
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

GET_LOGLEVEL = os.environ['LOG_LEVEL']
LOGLEVEL = logging.INFO
if GET_LOGLEVEL.lower() == "info":
    LOGLEVEL = logging.INFO
elif GET_LOGLEVEL.lower() == "error":
    LOGLEVEL = logging.ERROR
elif GET_LOGLEVEL.lower() == "debug":
    LOGLEVEL = logging.DEBUG

logging.basicConfig(level=LOGLEVEL, format='%(asctime)s %(levelname)s %(message)s')
logging.info('Started ginlong-solis-api-connector')

schedule.every(5).minutes.at(':00').do(main).run()

while True:
    if NEXT_RUN_YES == 1:
        next_run = schedule.next_run().strftime('%d/%m/%Y %H:%M:%S')
        logging.info('Next run is scheduled at %s', next_run)
        NEXT_RUN_YES = 0
    schedule.run_pending()
    time.sleep(1)
