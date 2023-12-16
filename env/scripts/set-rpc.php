<?php

if($_GET["cmd"]=="on")
{
  exec('wget "http://server.dom:8080/jsonrpc?request={%22jsonrpc%22:%222.0%22,%22method%22:%22Addons.ExecuteAddon%22,%22params%22:{%22addonid%22:%22script.json-cec%22,%22params%22:{%22command%22:%22activate%22}},%22id%22:1}" -q -O /dev/null');
}
else if($_GET["cmd"]=="off")
{
  exec('wget "http://server.dom:8080/jsonrpc?request={%22jsonrpc%22:%222.0%22,%22method%22:%22Addons.ExecuteAddon%22,%22params%22:{%22addonid%22:%22script.json-cec%22,%22params%22:{%22command%22:%22standby%22}},%22id%22:1}" -q -O /dev/null');
}
else
{
  exec('wget "http://server.dom:8080/jsonrpc?request={%20%22jsonrpc%22:%20%222.0%22,%20%22method%22:%20%22Input.ExecuteAction%22,%20%22params%22:%20{%20%22action%22:%20%22'.$_GET["cmd"].'%22%20},%20%22id%22:%201%20}" -q -O /dev/null');
}

?>