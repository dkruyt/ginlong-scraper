FROM python:alpine

ARG VERSION
ARG BUILD_DATE
ARG VCS_REF

LABEL maintainer="Gentleman1983, TobiO79" \
  org.opencontainers.image.created=$BUILD_DATE \
  org.opencontainers.image.url="https://github.com/Gentleman1983/ginlong_solis_api_connector" \
  org.opencontainers.image.source="https://github.com/Gentleman1983/ginlong_solis_api_connector" \
  org.opencontainers.image.version=$VERSION \
  org.opencontainers.image.revision=$VCS_REF \
  org.opencontainers.image.vendor="Gentleman1983" \
  org.opencontainers.image.title="ginlong-solis-api-connector" \
  org.opencontainers.image.description="Fetches API data from Solis Cloud API and outputs it to influxdb, pvoutput or mqtt" \
  org.opencontainers.image.licenses="GPL-3.0"

ENV LOG_LEVEL="INFO"

ENV SOLIS_CLOUD_API_KEY_ID=""
ENV SOLIS_CLOUD_API_KEY_SECRET=""
ENV SOLIS_CLOUD_API_URL="https://www.soliscloud.com"
ENV SOLIS_CLOUD_API_PORT="13333"
ENV SOLIS_CLOUD_API_INVERTER_ID="0"
ENV SOLIS_CLOUD_API_OVERRIDE_SINGLE_PHASE_INVERTER=""
ENV SOLIS_CLOUD_API_NUMBER_RETRIES="3"
ENV SOLIS_CLOUD_API_RETRIES_WAIT_S="1"

ENV USE_INFLUX="false"
ENV INFLUX_DATABASE="influxdb"
ENV INFLUX_SERVER="localhost"
ENV INFLUX_PORT="8086"
ENV INFLUX_PASSWORD=""
ENV INFLUX_USER=""
ENV INFLUX_MEASUREMENT="PV"

ENV USE_PVOUTPUT="false"
ENV PVOUTPUT_API_KEY=""
ENV PVOUTPUT_SYSTEM_ID=""
ENV PVOUTPUT_EXTENDED_V7=""
ENV PVOUTPUT_EXTENDED_V8=""
ENV PVOUTPUT_EXTENDED_V9=""
ENV PVOUTPUT_EXTENDED_V10=""
ENV PVOUTPUT_EXTENDED_V11=""
ENV PVOUTPUT_EXTENDED_V12=""

ENV USE_MQTT="false"
ENV MQTT_CLIENT_ID="pv"
ENV MQTT_SERVER="localhost"
ENV MQTT_USERNAME=""
ENV MQTT_PASSWORD=""
ENV MQTT_TOPIC="topic"
ENV MQTT_PORT="1883" 

ENV TZ=""

RUN apk add -U tzdata

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ginlong_solis_api_connector.py ./

CMD [ "python", "./ginlong_solis_api_connector.py" ]
