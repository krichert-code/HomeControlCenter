    function updateCurrentTemperature()
    {
		var xmlhttp;
		
		if (window.XMLHttpRequest)
		{
		  //code for IE7+, Firefox, Chrome, Opera, Safari
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
		 document.getElementById('heater').innerHTML=xmlhttp.responseText;
		    }
		}
		xmlhttp.open("GET","heater/heater.php",true);
		xmlhttp.send(null);
       }


