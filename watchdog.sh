#! /bin/sh

STATUS=$(curl -I http://192.168.1.3 2>/dev/null | grep HTTP | awk "{print \$2}"); if [ "$STATUS" = "200" ]; then echo "OK: $STATUS" >> /root/cron_test.log; else /usr/sbin/reboot ; fi
