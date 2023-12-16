<?php
    if($_GET['action']=='garage')
    {
	echo exec('cat /var/www/html/status/garage');
    }

    if($_GET['action']=='maingate')
    {
	echo exec('cat /var/www/html/status/maingate');
    }

    if($_GET['action']=='water')
    {
	echo exec('cat /var/www/html/status/water');
    }

    if($_GET['action']=='autowater')
    {
	$autowater = exec('cat /etc/cron.d/autowater | grep autowater.sh');
	$parts =  explode(" ", $autowater);
	$autowaterSettings = exec('cat /var/www/html/settings/water');
	$parts1 =  explode(" ", $autowaterSettings);

	echo $parts[0]." ".$parts[1]." ".$parts[4]." ".$parts1[0]." ".$parts1[1]." ".$parts1[2];
    }


    if($_GET['action']=='heatSettings')
    {
	echo exec('cat /var/www/html/settings/heat');
    }

?>