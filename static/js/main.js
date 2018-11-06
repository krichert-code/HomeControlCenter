function OpenDoor()
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

 if (confirm('Na pewno chcesz otworzyć/zamknąć garaż ?')) 
 {
   xmlhttp.open("GET", "scripts/set-data.php?action=garage", true);
   xmlhttp.send(null);
 }
}

function OpenGate()
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

 if (confirm('Chcesz otworzyć bramę wjazdow na stałe ?')) 
 {
   xmlhttp.open("GET", "scripts/set-data.php?action=maingate&stop=1", true);
   xmlhttp.send(null);
 }
 else
 {
   xmlhttp.open("GET", "scripts/set-data.php?action=maingate&stop=0", true);
   xmlhttp.send(null);
 }
}

function OnOffWater(onId)
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

 xmlhttp.open("GET", "scripts/set-data.php?action=water&arg1="+onId, true);
 xmlhttp.send(null);
}


function GetPanelInfo()
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

 xmlhttp.onreadystatechange=function()
 {
   if(xmlhttp.readyState==4)
   {
      document.getElementById('panel').innerHTML=xmlhttp.responseText;
   }
 }
   xmlhttp.open("GET", "panel/panel.php", true);
   xmlhttp.send(null);
}


function updateCurrentGarageStatus(mobile)
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

 xmlhttp.onreadystatechange=function()
 {
  if(xmlhttp.readyState==4){
     var zm = this.responseText;
     var style = "url(ico/gate.png)";


     if(mobile==1 && zm==2)
     {
        document.getElementById('garage_txt').innerHTML="...Czekaj...";
        return;
     }
     else if(mobile==1)
     {
        document.getElementById('garage_txt').innerHTML="Garaż";
        return;
     }

     if(zm==2)
     {
         style="url(ico/gate_brake.png)";
         document.getElementById('garage').onclick= function() {alert("Akcja jest wykonywana");}
     }
     else
     {
          document.getElementById('garage').onclick= function() {  }
          style = "url(ico/gate.png)";
     }

     document.getElementById('garage').style.backgroundImage = style;
  }
 }

  xmlhttp.open("GET", "scripts/get-data.php?action=garage", true);
  xmlhttp.send(null);
}

function updateCurrentMainGateStatus(mobile)
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

 xmlhttp.onreadystatechange=function()
 {
  if(xmlhttp.readyState==4){
     var zm = this.responseText;
     var style = "url(ico/gate1.png)";


     if(mobile==1 && zm==2)
     {
        document.getElementById('gate_txt').innerHTML="...Czekaj...";
        return;
     }
     else if(mobile==1)
     {
        document.getElementById('gate_txt').innerHTML="Brama";
        return;
     }

     if(zm==2)
     {
         style="url(ico/gate1_brake.png)";
         document.getElementById('mainGate').onclick= function() {alert("Akcja jest wykonywana");}
     }
     else
     {
          document.getElementById('mainGate').onclick= function() {  }
          style = "url(ico/gate1.png)";
     }

     document.getElementById('mainGate').style.backgroundImage = style;
  }
 }

  xmlhttp.open("GET", "scripts/get-data.php?action=maingate", true);
  xmlhttp.send(null);
}