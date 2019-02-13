FROM python:3.6
MAINTAINER hanabusa-lab

ENV LC_ALL=C.UTF-8 LANG=C.UTF-8

RUN set -x && \
  : "install gcloud" && \
  apt-get update && \
  apt-get install -y curl python && \
  curl https://sdk.cloud.google.com | bash
ENV CONFIG=/root/.config/gcloud \
  PATH=/root/google-cloud-sdk/bin:$PATH

RUN set -x && \
  pip install -v pip-tools==1.9.0

WORKDIR /app
ADD ./requirements.txt requirements.txt
RUN set -x && \
  pip install -r ./requirements.txt

