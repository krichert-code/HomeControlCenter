<?php

  if($_GET['action']=='garage')
  {
  // Status :
  // 0 - close/off
  // 1 - open/on
  // 2 - in progress

    $zm =  exec('cat /var/www/html/status/garage');
    if($zm==2)
    {
	//action in proggress
	echo $zm;
    }
    else
    {
	exec('echo "2" > /var/www/html/status/garage');
        exec('wget -O /dev/null http://switch.dom/gate0');
	sleep(17);
	exec('echo "0" > /var/www/html/status/garage');
	echo "0";
    }
  }

  if($_GET['action']=='maingate')
  {
  // Status :
  // 0 - close/off
  // 1 - open/on
  // 2 - in progress

    $zm =  exec('cat /var/www/html/status/maingate');
    if($zm==2)
    {
	//action in proggress
	echo $zm;
    }
    else
    {
	exec('echo "2" > /var/www/html/status/maingate');
        exec('wget -O /dev/null http://switch.dom/gate1');
	sleep(23);
        if($_GET['stop']=='1')
        {
          exec('wget -O /dev/null http://switch.dom/gate1');
   	  sleep(2);
          exec('wget -O /dev/null http://switch.dom/gate1');
   	  sleep(2);
          exec('wget -O /dev/null http://switch.dom/gate1');
        }
	exec('echo "0" > /var/www/html/status/maingate');
	echo "0";
    }
  }

  if($_GET['action']=='water')
  {
    // Status :
    //-1 - auto
    // 0 - off
    // 1 - water1
    // 2 - water2
    // 3 - water3

    if($_GET['arg1'] == 0)
    {
      exec('echo "0" > /var/www/html/status/water');
    }
    if($_GET['arg1'] == 1)
    {
      exec('echo "1" > /var/www/html/status/water');
    }
    if($_GET['arg1'] == 2)
    {
      exec('echo "2" > /var/www/html/status/water');
    }
    if($_GET['arg1'] == 3)
    {
      exec('echo "3" > /var/www/html/status/water');
    }

    exec('wget -O /dev/null http://switch.dom/water_off');

    if($_GET['arg1'] == 1)
    {
      exec('wget -O /dev/null http://switch.dom/water1_on');
    }

    if($_GET['arg1'] == 2)
    {
      exec('wget -O /dev/null http://switch.dom/water2_on');
    }

    if($_GET['arg1'] == 3)
    {
      exec('wget -O /dev/null http://switch.dom/water3_on');
    }
  }

  if($_GET['action']=='autowater')
  {
    // Status :
    //-1 - auto
    // 0 - off
    // 1 - water1
    // 2 - water2
    // 3 - water3

    exec('wget -O /dev/null http://switch.dom/water_off');

    exec('echo "0" > /var/www/html/status/water');

    //store data to settings
    $Ts = $_GET['Ts1'];
    $Ts = $Ts." ".$_GET['Ts2'];
    $Ts = $Ts." ".$_GET['Ts3'];
    $cmd = "echo -n '".$Ts."'> /var/www/html/settings/water";
    exec($cmd);

    //update cron settings
    exec('echo "SHELL=/bin/sh" > /var/www/html/settings/autowater');
    exec('echo "PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin" >> /var/www/html/settings/autowater');
    exec('echo "# m h dom mon dow user<>command" >> /var/www/html/settings/autowater');
    if(strlen($_GET['days']) > 0) $cmd = "echo '".$_GET['min']." ".$_GET['hour']." * * ".$_GET['days']." root bash /var/www/html/scripts/autowater.sh `cat /var/www/html/settings/water` > /var/www/html/logs/autowater' >> /var/www/html/settings/autowater";
    else $cmd = "echo '# auto water is off' >> /var/www/html/settings/autowater";
    exec($cmd);

    exec("sudo bash /var/www/html/scripts/autowater.sh");
    //restart cron service
    //exec('sudo restart cron');
  }

  if($_GET['action']=='SystemReset')
  {
    exec('wget -O /dev/null http://switch.dom/water_off');
    exec('sudo reboot');
  }

  if($_GET['action']=='heatSettings')
  {
    //store data to settings
    $params = $_GET['T1'];
    $params = $params.",".$_GET['T2'];
    $params = $params.",".$_GET['T3'];
    $params = $params.",".$_GET['T4'];
    $params = $params.",".$_GET['Hod1'];
    $params = $params.",".$_GET['Hod2'];
    $params = $params.",".$_GET['Hod3'];
    $params = $params.",".$_GET['Hdo1'];
    $params = $params.",".$_GET['Hdo2'];
    $params = $params.",".$_GET['Hdo3'];

    $params = $params.",".$_GET['HTab0'];
    $params = $params.",".$_GET['HTab1'];
    $params = $params.",".$_GET['HTab2'];
    $params = $params.",".$_GET['HTab3'];
    $params = $params.",".$_GET['HTab4'];
    $params = $params.",".$_GET['HTab5'];
    $params = $params.",".$_GET['HTab6'];

    $cmd = "echo -n '".$params."'> /var/www/html/settings/heat";
    exec($cmd);
  }
?>