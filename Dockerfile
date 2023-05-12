FROM python:alpine

ARG VERSION
ARG BUILD_DATE
ARG VCS_REF

LABEL maintainer="Gentleman1983, TobiO79" \
  org.opencontainers.image.created=$BUILD_DATE \
  org.opencontainers.image.url="https://github.com/Gentleman1983/ginlong-scraper" \
  org.opencontainers.image.source="https://github.com/Gentleman1983/ginlong-scraper" \
  org.opencontainers.image.version=$VERSION \
  org.opencontainers.image.revision=$VCS_REF \
  org.opencontainers.image.vendor="Gentleman1983" \:13333
  org.opencontainers.image.title="ginlong-solis-api-connector" \
  org.opencontainers.image.description="Fetches API data from Solis Cloud API and outputs it to influxdb, pvoutput or mqtt" \
  org.opencontainers.image.licenses="GPL-3.0"

ENV LOG_LEVEL="INFO"

ENV SOLIS_CLOUD_API_KEY_ID = ""
ENV SOLIS_CLOUD_API_KEY_SECRET = ""
ENV SOLIS_CLOUD_API_URL = "https://www.soliscloud.com"
ENV SOLIS_CLOUD_API_PORT = "13333"
ENV SOLIS_CLOUD_API_INVERTER_ID = ""

#ENV GINLONG_USERNAME=""
#ENV GINLONG_PASSWORD=""
#ENV GINLONG_DOMAIN="m.ginlong.com"
#ENV GINLONG_LANG="2"
#ENV GINLONG_DEVICE_ID=""

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

ENV USE_MQTT="false"
ENV MQTT_CLIENT_ID="pv"
ENV MQTT_SERVER="localhost"
ENV MQTT_USERNAME=""
ENV MQTT_PASSWORD=""

ENV TZ=""

RUN apk add -U tzdata

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ginlong-scraper.py ./

CMD [ "python", "./ginlong-scraper.py" ]
