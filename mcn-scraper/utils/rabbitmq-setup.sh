#!/bin/sh

rabbitmqctl add_user mcn 'mcn'
rabbitmqctl set_user_tags mcn monitoring
rabbitmqctl add_vhost mcn-scraper
rabbitmqctl set_permissions -p mcn-scraper mcn ".*" ".*" ".*"
