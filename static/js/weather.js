
    function updateCurrentWeather()
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
	        	document.getElementById('weather').innerHTML=xmlhttp.responseText;
		    }
		}
		xmlhttp.open("GET","weather",true);
		xmlhttp.send(null);
	}


    function updateWeatherForecast(param)
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
	        	document.getElementById('idx'+param).innerHTML=xmlhttp.responseText;
	    	}
		}
		xmlhttp.open("GET","forecast.php?index="+param,true);
		xmlhttp.send(null);
    }
