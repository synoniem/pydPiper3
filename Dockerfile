FROM arm32v6/python:3-alpine

WORKDIR /app
ADD requirements.txt /app
RUN apk update && apk add \
  python3-dev \
  py3-pip \
  py3-smbus \
  freetype-dev \
  jpeg-dev \
  ttf-dejavu \
  build-base \
  gcc \
  linux-headers \
  bash \
  py3-pillow && rm -rf /var/cache/apk/*
RUN pip3 uninstall PIL
RUN pip3 install -r requirements.txt
CMD /bin/bash
