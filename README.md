# ginlong-scraper

A python script that scrapes PV statistics from the Ginlong monitor pages and outputs it to influxdb, pvoutput or mqtt.

## Install

Install necessary python modules.

```
pip install paho-mqtt
pip install influxdb
```

Adjust the config. Set the outputs that are not needed to false.

```
# solis/ginlong portal config
username		= 'user@name' #your portal username
password 		= 'password' #your portal password
domain 			= 'monitoring.csisolar.com' #domain ginlong used multiple domains with same login but different versions, could change anytime. monitoring.csisolar.com, m.ginlong.com
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
```

Create a cron entry, every 5 min is ok, becuase the inverter logs also every 5 min.

```
*/5 *     * * *     user	/opt/solis-influx/ginlong-scraper.py > /dev/null 2>&1
```

## Bonus

The grafana-dashboard-example.json file you could import in to Grafana if you use the influx database. Then you can make a dashboard similar to this. 

![grafana](https://github.com/dkruyt/resources/raw/master/grafana-dashboard-ginlong-small.png)
