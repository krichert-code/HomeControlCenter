#!/usr/bin/perl
use strict;
use warnings;
use Time::Piece;

my $temp;
my $offset = 0;

my $file = `date +"%d-%m-%Y"`;
my $time = localtime;
my $line;
my $heater;
my @params = split "," , `cat /var/www/html/settings/heat`;
my $dayOfWeek = `date +"%u"` -1;
my $hour = `date +"%k"`;

my $margin = 0.2;

my $T1;
my $T2;
my $T3;
my $T4;
my $Hod1;
my $Hod2;
my $Hod3;
my $Hdo1;
my $Hdo2;
my $Hdo3;
my @HTab;
my $cmpTemp = 0;
my $mode = 0;

$T1 = $params[0];
$T2 = $params[1];
$T3 = $params[2];
$T4 = $params[3];

$Hod1 = $params[4];
$Hod2 = $params[5];
$Hod3 = $params[6];

$Hdo1 = $params[7];
$Hdo2 = $params[8];
$Hdo3 = $params[9];

$HTab[0] = $params[10];
$HTab[1] = $params[11];
$HTab[2] = $params[12];
$HTab[3] = $params[13];
$HTab[4] = $params[14];
$HTab[5] = $params[15];
$HTab[6] = $params[16];

$offset = $T4;
$temp=`cat /sys/devices/w1_bus_master1/28-0000071e5850/w1_slave | grep t=| cut -d"=" -f2`;
$temp = sprintf "%.1f", ($temp / 1000) + $offset;


# Check mode and temperature (1 - day, 0 - night)
#####################################################
if (($HTab[$dayOfWeek] & (1<<$hour)) != 0)
{
 $cmpTemp = $T1;
 $mode = "1";
}
else
{
 $cmpTemp = $T2;
 $mode = "0";
}
#####################################################

# Checkin condition to turn of heater.
# Turn on heater when tempature will be below cmpTemp
# Turn off heater only when temperature will be above cmpTemp + 0.2
#####################################################
$heater="1";
if($temp < $cmpTemp)
{
#  `wget -O /dev/null http://192.168.111.205/heat_on`
}
elsif($temp >= $cmpTemp + $margin)
{
 $heater="0";
# `wget -O /dev/null http://192.168.111.205/heat_off`
}
#####################################################

$line=$temp.",".$heater.",".$mode.",".$time->hms;

#print $line."\n".$cmpTemp;
`echo $line >> /HomeControlCenter/data/heater.csv`
