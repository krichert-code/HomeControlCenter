#!/bin/sh
#
# autowater.sh
#
# This script start automaticlly water sprinkler
#
#
# Status file :
#
# -1 - auto
#  0 - off
#  1 - water1
#  2 - water2
#  3 - water3

if [ $# -eq 0 ]
then
  if [ -e /etc/cron.d/autowater ]
  then
    diffc=`cmp /etc/cron.d/autowater  /var/www/html/settings/autowater | wc -l`
  else
    diffc=1
  fi

  if [ $diffc -gt 0 ]
  then
    cp /var/www/html/settings/autowater /etc/cron.d
  fi

  exit
fi

if [ $# != 3 ]
then
  echo "Wrong number of parameters"
  exit
fi


rain=`cat /var/www/html/settings/rain`

if [ $rain -gt 0 ]
then
  echo "Blocked by rain"
  exit
fi

echo "Set auto mode"
echo "-1" > /var/www/html/status/water


echo "Auto sprinkler times:"
echo "Section 1: $1 min"
echo "Section 2: $2 min"
echo "Section 3: $3 min"


date +"%m-%d-%y %T :Turn on section 1 - time $1 minutes"
wget -O /dev/null http://switch.dom/water_off
wget -O /dev/null http://switch.dom/water1_on
sleep $1m

date +"%m-%d-%y %T :Turn on section 2 - time $2 minutes"
wget -O /dev/null http://switch.dom/water_off
wget -O /dev/null http://switch.dom/water2_on
sleep $2m

date +"%m-%d-%y %T :Turn on section 3 - time $3 minutes"
wget -O /dev/null http://switch.dom/water_off
wget -O /dev/null http://switch.dom/water3_on
sleep $3m

wget -O /dev/null http://switch.dom/water_off


date +"%m-%d-%y %T :Clear auto mode"
echo "0" > /var/www/html/status/water
