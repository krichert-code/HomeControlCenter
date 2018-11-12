#!/bin/sh
#
# speaker.sh
#
# This script start automaticlly speakers
#
# PINS
# gpio 0 - Power (turn on speakers)
# gpio 2 - change volume (needed to activate speakers)

speaker_off=0

for i in {1..12}
do

speaker_state=`gpio read 0`
player_state=`wget -q -O -  "http://192.168.1.3:8080/jsonrpc?request={%22jsonrpc%22:%222.0%22,%22method%22:%22Player.GetActivePlayers%22,%22id%22:1}" | grep -c "video\|audio"`

#mplayer_killed=0

if [ $player_state == 1 ]
then
 #turn on speakes if there are off
 if [ $speaker_state == 0 ]
 then
  speaker_off=0
  gpio readall
  gpio write 0 1
  sleep 1.2
  gpio write 2 1
  sleep 0.8
  gpio write 2 0
 fi
elif [ $speaker_state == 1 ]
 #turn off speakers if there are on (after ~(5sec * iterator) without music source)
 then
  speaker_off=`expr $speaker_off + 1`
  if [ $speaker_off == 10 ]
  then
    gpio write 0 0
  fi
fi

sleep 5
done