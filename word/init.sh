#!/bin/bash
#
# docker-compose の起動前の環境設定を行います。

cat <<EOF > .env
USER_ID=$(id -u)
GROUP_ID=$(id -g)
TIME_ZONE=Asia/Tokyo
EOF
