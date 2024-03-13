# Version change log
This document provides an overview to the changes on the different releases...

## NEXT
* t.b.d.

## 3.0.0
> [!WARNING]  
> In this update we refactored all actual and upcoming number fields to provide data in float values. There may be the
> need to update your existing InfluxDB instance to handle the new data types.
* Updated the Dockerhub repository on `README.md`, to not point to the [old dkruyt API scraper images](https://hub.docker.com/repository/docker/dkruyt/ginlong-scraper) ([#51](https://github.com/Gentleman1983/ginlong_solis_api_connector/issues/51))
* Added publishing to Dockerhub repository [gentleman1983/ginlong-solis-api-connector](https://hub.docker.com/repository/docker/gentleman1983/ginlong-solis-api-connector) on release ([#55](https://github.com/Gentleman1983/ginlong_solis_api_connector/issues/55))
* Publishing task to Dockerhub should publish [SBOM](https://www.cisa.gov/sbom), too ([#57](https://github.com/Gentleman1983/ginlong_solis_api_connector/issues/57))
* Add Mend renovate bot to repository ([#56](https://github.com/Gentleman1983/ginlong_solis_api_connector/issues/56))
* Fixed parsing issues regarding api update from March 4th, 2024. ([#68](https://github.com/Gentleman1983/ginlong_solis_api_connector/issues/68))
* Pinned the data units regarding the dynamic units on Ginlong API. ([#13](https://github.com/Gentleman1983/ginlong_solis_api_connector/issues/13))

## 2.4.0
* Added `CHANGELOG.md` document to have central document for changes. ([#38](https://github.com/Gentleman1983/ginlong_solis_api_connector/issues/38))
* Fixed issue regarding bad gateways. ([#46](https://github.com/Gentleman1983/ginlong_solis_api_connector/issues/46))
  * Added option to configure number and timeout between retries.
* Added the fields `pA`, `pB` and `PC` to change list to update according to API changes on end of November 2023.

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
