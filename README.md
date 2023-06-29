![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/Gentleman1983/ginlong_solis_api_connector?sort=semver&style=plastic)
![GitHub workflow (pylint)](https://img.shields.io/github/actions/workflow/status/Gentleman1983/ginlong_solis_api_connector/pylint.yml?label=pylint&style=plastic)
![GitHub license](https://img.shields.io/github/license/Gentleman1983/ginlong_solis_api_connector?style=plastic)
![All Contributors](https://img.shields.io/github/all-contributors/Gentleman1983/ginlong_solis_api_connector?style=plastic)
![GitHub stars](https://img.shields.io/github/stars/Gentleman1983/ginlong_solis_api_connector?style=plastic)

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

| Environment variable                            | Required | Description                                                                                                                          | Default value                  |
|-------------------------------------------------|----------|--------------------------------------------------------------------------------------------------------------------------------------|--------------------------------|
| LOG_LEVEL                                       | No       | Logging level (ERROR, INFO, DEBUG)                                                                                                   | `INFO`                         |
| SOLIS_CLOUD_API_KEY_ID                          | Yes      | API Key ID                                                                                                                           | *empty*                        |
| SOLIS_CLOUD_API_KEY_SECRET                      | Yes      | API Key Secret                                                                                                                       | *empty*                        |
| SOLIS_CLOUD_API_URL                             | No       | API URL                                                                                                                              | `https://www.soliscloud.com`   |
| SOLIS_CLOUD_API_PORT                            | No       | API Port                                                                                                                             | `13333`                        |
| SOLIS_CLOUD_API_INVERTER_ID                     | No       | Ginlong Solis device ID<br/>(only required if auto-detect fails or if you have more than one device)                                 | `0` or *empty*                 |
| SOLIS_CLOUD_API_OVERRIDE_SINGLE_PHASE_INVERTER  | No       | Override to provide correct calculations for single phase inverters if Solis Cloud API provides wrong data. Simply switch to `true`  | *empty*                        |
| SOLIS_CLOUD_API_NUMBER_RETRIES                  | No       | Number of retries to fetch an API endpoint                                                                                           | `3`                            |
| SOLIS_CLOUD_API_RETRIES_WAIT_S                  | No       | Timeout between retries                                                                                                              | `1`                            |
| USE_INFLUX                                      | No       | Set to true if you want to use InfluxDB as output                                                                                    | `false`                        |
| INFLUX_DATABASE                                 | No       | InfluxDB DB name                                                                                                                     | `influxdb`                     |
| INFLUX_SERVER                                   | No       | InfluxDB server                                                                                                                      | `localhost`                    |
| INFLUX_PORT                                     | No       | InfluxDB server port                                                                                                                 | `8086`                         |
| INFLUX_USER                                     | No       | InfluxDB User                                                                                                                        | *empty*                        |
| INFLUX_PASSWORD                                 | No       | InfluxDB Password                                                                                                                    | *empty*                        |
| INFLUX_MEASUREMENT                              | No       | InfluxDB measurement type                                                                                                            | `PV`                           |
| USE_PVOUTPUT                                    | No       | Set to true if you want to use PvOutput as output                                                                                    | `false`                        |
| PVOUTPUT_API_KEY                                | No       | PvOutput API key                                                                                                                     | *empty*                        |
| PVOUTPUT_SYSTEM_ID                              | No       | PvOutput system ID                                                                                                                   | *empty*                        |
| PVOUTPUT_EXTENDED_V7                            | No       | Set Extendet Output v7 to this API Key from inverterDetail (leave blank if not donated)                                              | *empty*                        |
| PVOUTPUT_EXTENDED_V8                            | No       | Set Extendet Output v8 to this API Key from inverterDetail (leave blank if not donated)                                              | *empty*                        |
| PVOUTPUT_EXTENDED_V9                            | No       | Set Extendet Output v9 to this API Key from inverterDetail (leave blank if not donated)                                              | *empty*                        |
| PVOUTPUT_EXTENDED_V10                           | No       | Set Extendet Output v10 to this API Key from inverterDetail (leave blank if not donated)                                             | *empty*                        |
| PVOUTPUT_EXTENDED_V11                           | No       | Set Extendet Output v11 to this API Key from inverterDetail (leave blank if not donated)                                             | *empty*                        |
| PVOUTPUT_EXTENDED_V12                           | No       | Set Extendet Output v12 to this API Key from inverterDetail (leave blank if not donated)                                             | *empty*                        |
| USE_MQTT                                        | No       | Set to true if you want to use MQTT as output                                                                                        | `false`                        |
| MQTT_CLIENT_ID                                  | No       | MQTT client ID                                                                                                                       | `pv`                           |
| MQTT_SERVER                                     | No       | MQTT server                                                                                                                          | `localhost`                    |
| MQTT_USERNAME                                   | No       | MQTT username                                                                                                                        | *empty*                        |
| MQTT_PASSWORD                                   | No       | MQTT password                                                                                                                        | *empty*                        |
| MQTT_PORT                                       | No       | MQTT port default 1883                                                                                                               | `1883`                         |
| MQTT_TOPIC                                      | No       | MQTT topic root, fulltopic will by MQTT_Topic / MQTT_Client_ID                                                                       | `topic`                        |     
| TZ                                              | No       | TimeZone e.g Australia/Sydney                                                                                                        | *empty*                        |

Note that if you have more than 1 device - then it is not readily apparent where to get the Device ID
In that case - setup the script, and set `LOG_LEVEL` to `DEBUG`, then view the logs and search for deviceId - 
this will list the IDs of each inverter.

## Bonus

The grafana-dashboard-example.json file you could import in to Grafana if you use the influx database. Then you can make a dashboard similar to this.

![grafana](https://github.com/dkruyt/resources/raw/master/grafana-dashboard-ginlong-small.png)

# Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/TobiO79"><img src="https://avatars.githubusercontent.com/u/30373938?v=4?s=100" width="100px;" alt="Tobias Otto"/><br /><sub><b>Tobias Otto</b></sub></a><br /><a href="https://github.com/Gentleman1983/ginlong_solis_api_connector/commits?author=TobiO79" title="Tests">⚠️</a> <a href="https://github.com/Gentleman1983/ginlong_solis_api_connector/commits?author=TobiO79" title="Code">💻</a> <a href="#maintenance-TobiO79" title="Maintenance">🚧</a> <a href="https://github.com/Gentleman1983/ginlong_solis_api_connector/pulls?q=is%3Apr+reviewed-by%3ATobiO79" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Gentleman1983"><img src="https://avatars.githubusercontent.com/u/1020222?v=4?s=100" width="100px;" alt="Christian Otto"/><br /><sub><b>Christian Otto</b></sub></a><br /><a href="https://github.com/Gentleman1983/ginlong_solis_api_connector/commits?author=Gentleman1983" title="Tests">⚠️</a> <a href="https://github.com/Gentleman1983/ginlong_solis_api_connector/commits?author=Gentleman1983" title="Code">💻</a> <a href="#maintenance-Gentleman1983" title="Maintenance">🚧</a> <a href="https://github.com/Gentleman1983/ginlong_solis_api_connector/pulls?q=is%3Apr+reviewed-by%3AGentleman1983" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/petermdevries"><img src="https://avatars.githubusercontent.com/u/15040708?v=4?s=100" width="100px;" alt="Peter de Vries"/><br /><sub><b>Peter de Vries</b></sub></a><br /><a href="https://github.com/Gentleman1983/ginlong_solis_api_connector/issues?q=author%3Apetermdevries" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Flecky13"><img src="https://avatars.githubusercontent.com/u/57505680?v=4?s=100" width="100px;" alt="Pedro"/><br /><sub><b>Pedro</b></sub></a><br /><a href="https://github.com/Gentleman1983/ginlong_solis_api_connector/issues?q=author%3AFlecky13" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/philicibine"><img src="https://avatars.githubusercontent.com/u/16887758?v=4?s=100" width="100px;" alt="philicibine"/><br /><sub><b>philicibine</b></sub></a><br /><a href="https://github.com/Gentleman1983/ginlong_solis_api_connector/issues?q=author%3Aphilicibine" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/MetPhoto"><img src="https://avatars.githubusercontent.com/u/2766363?v=4?s=100" width="100px;" alt="Mark"/><br /><sub><b>Mark</b></sub></a><br /><a href="https://github.com/Gentleman1983/ginlong_solis_api_connector/issues?q=author%3AMetPhoto" title="Bug reports">🐛</a></td>
    </tr>
  </tbody>
  <tfoot>
    <tr>
      <td align="center" size="13px" colspan="7">
        <img src="https://raw.githubusercontent.com/all-contributors/all-contributors-cli/1b8533af435da9854653492b1327a23a4dbd0a10/assets/logo-small.svg">
          <a href="https://all-contributors.js.org/docs/en/bot/usage">Add your contributions</a>
        </img>
      </td>
    </tr>
  </tfoot>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
