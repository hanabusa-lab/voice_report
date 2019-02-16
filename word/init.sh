#!/bin/bash

cat <<EOF > .env
USER_ID=$(id -u)
GROUP_ID=$(id -g)
TIME_ZONE=Asia/Tokyo
EOF
