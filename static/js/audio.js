
    function ajaxPlayer(id,arg)
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
	    if(xmlhttp.readyState==4 && id==-2)
	    {
		setMp3PlayerContent("");
	    }
	}
	xmlhttp.open("GET","mplayer.php?id="+id+"&arg="+arg,true);
	xmlhttp.send(null);
    }

    function ajaxVolume(volume)
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
	    if((xmlhttp.readyState==4) && (volume == 0))
	    {
	        document.getElementById('progress-bar').style.width=xmlhttp.responseText+"px";
	    }
	}
	xmlhttp.open("GET","volume.php?volume="+volume,true);
	xmlhttp.send(null);
    }

    function changeVolume(volume)
    {
        var current = parseInt(document.getElementById('progress-bar').style.width);

        if(volume>0) current = current + 24;
	else  current = current - 24;

        if(current>470) current = 470;
        if(current<0) current = 0;
        document.getElementById('progress-bar').style.width=current+"px";
        ajaxVolume(volume);
    }


//MP3

    

    function playAll()
    {
	var dir;
	
	dir = document.getElementById('currentDir').innerText;
	ajaxPlayer(dir);    
    }
    
    function setMp3PlayerContent(directory,mobile)
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
	      document.getElementById('Mp3Player').innerHTML=xmlhttp.responseText;
	    }
	}
	xmlhttp.open("GET","GetElements.php?dir="+directory+"&mobile="+mobile,true);
	xmlhttp.send(null);
    }
    
    function ajaxNextPrev(direction)
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
	      //document.getElementById('debug').innerHTML=xmlhttp.responseText;
	    }
	}
	//start player
	xmlhttp.open("GET","next_prev.php?direction="+direction,true);
	xmlhttp.send(null);
    }
    
