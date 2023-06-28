# Version change log
This document provides an overview to the changes on the different releases...

## NEXT
* Added `CHANGELOG.md` document to have central document for changes. ([#38](https://github.com/Gentleman1983/ginlong_solis_api_connector/issues/38))
* Fixed issue regarding bad gateways. ([#46](https://github.com/Gentleman1983/ginlong_solis_api_connector/issues/46))
  * Added option to configure number and timeout between retries. 

## 2.3.1
* Fixed issue on error handling on the `SOLIS_CLOUD_API_INVERTER_ID` parameter. ([#24](https://github.com/Gentleman1983/ginlong_solis_api_connector/issues/24))
* Fixed possible index out of bounds exception. ([#24](https://github.com/Gentleman1983/ginlong_solis_api_connector/issues/24))
* Added support for all contributors bot. ([#2](https://github.com/Gentleman1983/ginlong_solis_api_connector/issues/2), [#26](https://github.com/Gentleman1983/ginlong_solis_api_connector/issues/26), [#31](https://github.com/Gentleman1983/ginlong_solis_api_connector/issues/31))

## 2.3.0
* Added option to override detection for single phase inverters. ([#14](https://github.com/Gentleman1983/ginlong_solis_api_connector/issues/14))
* Fixed calculation on some data fields to fix issues on monitoring. ([#16](https://github.com/Gentleman1983/ginlong_solis_api_connector/issues/16), [#22](https://github.com/Gentleman1983/ginlong_solis_api_connector/issues/22))
* Fixed mixing up of some PVoutput values (`v3` & `v4`). ([#17](https://github.com/Gentleman1983/ginlong_solis_api_connector/issues/17))
* Fixed issue on influx db where some values where interpreted as integers instead of floats when value is `0`. This lead to problems in data import, e.g. during the nighttime. ([#18](https://github.com/Gentleman1983/ginlong_solis_api_connector/issues/18))

## 2.2.0
* Added configurability for optional PVoutput fields `pv7` to `pv12` for subscribers of PVoutput. ([#4](https://github.com/Gentleman1983/ginlong_solis_api_connector/issues/4))
* Fixed missing usage of inverter ID ENV value. ([#8](https://github.com/Gentleman1983/ginlong_solis_api_connector/issues/8))
* Fixed some conversion issues on integer ENV values like inverter ID, ports, etc. ([#6](https://github.com/Gentleman1983/ginlong_solis_api_connector/issues/6))
* Fixed some PyLint issues or marked them as false positives or as better readable containing them on source code.

## 2.1.0
* Added functionality to handle single phase inverters ([#3](https://github.com/Gentleman1983/ginlong_solis_api_connector/issues/3))
* Added option to support multiple inverters

## 2.0.0
* Added functionality to connect to Solis Cloud API.