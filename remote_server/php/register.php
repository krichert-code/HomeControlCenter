<?php
$servername = "localhost";
$username = "id21363354_kwiatowa";
$password = "Kwiatowa13!";
$dbname = "id21363354_hcc";
$errorCode = 0;

// get device id
$data = file_get_contents("php://input");
$json_obj = json_decode($data);


$id = base64_decode($json_obj->{'data'});
$id = substr($id,0,8);
$id = intval($id);


if (!class_exists('mysqli')) {
    $errorCode=1;
    exit(0);
}


$conn = new mysqli($servername, $username, $password, $dbname);


// Check connection
if ($conn->connect_error) {
    $errorCode=2;
    exit(0);
}

$sql = "SELECT * FROM connections where id=$id";
$result = $conn->query($sql);


if ($result->num_rows == 0) {
    //insert
    $sql = "INSERT INTO connections(id, req, res, reqAvailable, resAvailable) values($id,'','',false,false)";
    $result = $conn->query($sql);

}

if ($json_obj->{'type'} == 1) {
    //response ready
    $sql = "UPDATE connections SET resAvailable=true, reqAvailable=false, res='".$json_obj->{'data'}."' where id=$id";
    $result = $conn->query($sql);
}
else {
    //reset 
    $sql = "UPDATE connections SET resAvailable=false, reqAvailable=false where id=$id";
    //$result = $conn->query($sql);
}


//wait for request
$loop = 5;
while ($loop > 0) {
    $sql = "SELECT * FROM connections where id=$id";
    $result = $conn->query($sql);
    $row = $result->fetch_assoc();

    sleep(1);

    if ($row['reqAvailable'] == true) {
        //process request
        echo $row['req'];
        break;
    }
    $loop--;
}



?>
