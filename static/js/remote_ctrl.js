var state = 0;

function OnOff()
{
 var xmlhttp;
 if (window.XMLHttpRequest)
 {
  // code for IE7+, Firefox, Chrome, Opera, Safari
  xmlhttp=new XMLHttpRequest();
 }
 else
 {
  alert("Your browser does not support XMLHTTP!");
 }

 if(this.state == 0)
 {
    this.state = 1;
    xmlhttp.open("GET", "http://192.168.1.3/scripts/set-rpc.php?cmd=on", true);
 }
 else
 {
    this.state = 0;
     xmlhttp.open("GET", "http://192.168.1.3/scripts/set-rpc.php?cmd=off", true);
 }

 xmlhttp.send(null);
}

function GenericCmd(cmd)
{
 var xmlhttp;
 if (window.XMLHttpRequest)
 {
  // code for IE7+, Firefox, Chrome, Opera, Safari
  xmlhttp=new XMLHttpRequest();
 }
 else
 {
  alert("Your browser does not support XMLHTTP!");
 }

 xmlhttp.open("GET", "http://192.168.1.3/scripts/set-rpc.php?cmd="+cmd, true);
 xmlhttp.send(null);
}
