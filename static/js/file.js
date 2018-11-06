
    
    function setFileContent(directory, mobile)
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
	      document.getElementById('FileContent').innerHTML=xmlhttp.responseText;
	    }
	}
	xmlhttp.open("GET","GetElements.php?dir="+directory+"&mobile="+mobile,true);
	xmlhttp.send(null);
    }
    
