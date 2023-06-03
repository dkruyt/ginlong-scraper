# ginlong-solis-api-connector

Fetches API data from Solis Cloud API and outputs it to influxdb, pvoutput or mqtt. Based on [ginlong-scraper by dkruyt](https://github.com/dkruyt/ginlong-scraper).

https://hub.docker.com/repository/docker/dkruyt/ginlong-scraper

There is a possibility it also works with the following inverters: Omnik Solar, Solarman and Trannergy Inverters

You can also move the environment variables into an ENV file and invoke that on the commandline when 
invoking the docker image.

In the case of two inverters (see note below) once you have the deviceid you can set up two seperate docker containers
and just vary the deviceId in the environment variables.

## Requirements
* You have to order the Solis Cloud API access like described [here](https://solis-service.solisinverters.com/support/solutions/articles/44002212561-api-access-soliscloud).
* You have to know the Solis Cloud API `KeyID` and `KeySecret`.

## Configuration

### Environment variables

| Environment variable        | Required  | Description                                                                                          | Default value                |
|-----------------------------|-----------|------------------------------------------------------------------------------------------------------|------------------------------|
| LOG_LEVEL                   | No        | Logging level (ERROR, INFO, DEBUG)                                                                   | `INFO`                       |
| SOLIS_CLOUD_API_KEY_ID      | Yes       | API Key ID                                                                                           | *empty*                      |
| SOLIS_CLOUD_API_KEY_SECRET  | Yes       | API Key Secret                                                                                       | *empty*                      |
| SOLIS_CLOUD_API_URL         | No        | API URL                                                                                              | `https://www.soliscloud.com` |
| SOLIS_CLOUD_API_PORT        | No        | API Port                                                                                             | `13333`                      |
| SOLIS_CLOUD_API_INVERTER_ID | No        | Ginlong Solis device ID<br/>(only required if auto-detect fails or if you have more than one device) | *empty*                      |
| USE_INFLUX                  | No        | Set to true if you want to use InfluxDB as output                                                    | `false`                      |
| INFLUX_DATABASE             | No        | InfluxDB DB name                                                                                     | `influxdb`                   |
| INFLUX_SERVER               | No        | InfluxDB server                                                                                      | `localhost`                  |
| INFLUX_PORT                 | No        | InfluxDB server port                                                                                 | `8086`                       |
| INFLUX_USER                 | No        | InfluxDB User                                                                                        | *empty*                      |
| INFLUX_PASSWORD             | No        | InfluxDB Password                                                                                    | *empty*                      |
| INFLUX_MEASUREMENT          | No        | InfluxDB measurement type                                                                            | `PV`                         |
| USE_PVOUTPUT                | No        | Set to true if you want to use PvOutput as output                                                    | `false`                      |
| PVOUTPUT_API_KEY            | No        | PvOutput API key                                                                                     | *empty*                      |
| PVOUTPUT_SYSTEM_ID          | No        | PvOutput system ID                                                                                   | *empty*                      |
| PVOUTPUT_EXTENDED_V7        | No        | Set Extendet Output v7 to this API Key from inverterDetail (leave blank if not donated)              | *empty*                      |
| PVOUTPUT_EXTENDED_V8        | No        | Set Extendet Output v8 to this API Key from inverterDetail (leave blank if not donated)              | *empty*                      |
| PVOUTPUT_EXTENDED_V9        | No        | Set Extendet Output v9 to this API Key from inverterDetail (leave blank if not donated)              | *empty*                      |
| PVOUTPUT_EXTENDED_V10       | No        | Set Extendet Output v10 to this API Key from inverterDetail (leave blank if not donated)             | *empty*                      |
| PVOUTPUT_EXTENDED_V11       | No        | Set Extendet Output v11 to this API Key from inverterDetail (leave blank if not donated)             | *empty*                      |
| PVOUTPUT_EXTENDED_V12       | No        | Set Extendet Output v12 to this API Key from inverterDetail (leave blank if not donated)             | *empty*                      |
| USE_MQTT                    | No        | Set to true if you want to use MQTT as output                                                        | `false`                      |
| MQTT_CLIENT_ID              | No        | MQTT client ID                                                                                       | `pv`                         |
| MQTT_SERVER                 | No        | MQTT server                                                                                          | `localhost`                  |
| MQTT_USERNAME               | No        | MQTT username                                                                                        | *empty*                      |
| MQTT_PASSWORD               | No        | MQTT password                                                                                        | *empty*                      |
| TZ                          | No        | TimeZone e.g Australia/Sydney                                                                        | *empty*                      |

Note that if you have more than 1 device - then it is not readily apparent where to get the Device ID
In that case - setup the script, and set `LOG_LEVEL` to `DEBUG`, then view the logs and search for deviceId - 
this will list the IDs of each inverter.

## Bonus

The grafana-dashboard-example.json file you could import in to Grafana if you use the influx database. Then you can make a dashboard similar to this.

![grafana](https://github.com/dkruyt/resources/raw/master/grafana-dashboard-ginlong-small.png)
