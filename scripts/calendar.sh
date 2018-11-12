#!/bin/sh
#
# calendar.sh
#
# This script start get data from goolge calendar and store them in json file
#


minDate=`date +%Y-%m-%d --date="+0 day"`
maxDate=`date +%Y-%m-%d --date="+7 day"`


http="https://www.googleapis.com/calendar/v3/calendars/krzysiek.richert@gmail.com/events?timeMax="$maxDate"T00%3A00%3A00-07%3A00&timeMin="$minDate"T00%3A00%3A00-07%3A00&key=AIzaSyDepBebtgRz7DIOR60j4Uu0Y-CnOpy22fo"
wget -O /HomeControlCenter/data/mycal.json $http


http="https://www.googleapis.com/calendar/v3/calendars/polish@holiday.calendar.google.com/events?timeMax="$maxDate"T00%3A00%3A00-07%3A00&timeMin="$minDate"T00%3A00%3A00-07%3A00&key=AIzaSyDepBebtgRz7DIOR60j4Uu0Y-CnOpy22fo"
wget -O /HomeControlCenter/data/holidays.json $http
