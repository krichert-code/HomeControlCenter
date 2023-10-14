<?php
$servername = "localhost";
$username = "id21363354_kwiatowa";
$password = "Kwiatowa13!";
$dbname = "id21363354_hcc";
$errorCode = 0;

// get device id
$data = file_get_contents("php://input");

$id = base64_decode($data);
$id = substr($id,0,8);
$id = intval($id);


// send request
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
$row = $result->fetch_assoc();

if ($result->num_rows == 0) {
    //insert
    $sql = "INSERT INTO connections(id, req, res, reqAvailable, resAvailable) values($id,'".$data."','',true,false)";
    $result = $conn->query($sql);
}

// insert request
if ($row['reqAvailable'] == false) {
    $sql = "UPDATE connections SET req='".$data."', reqAvailable=true, resAvailable=false where id=$id";
    $result = $conn->query($sql);

    //wait for response
    $output = "";
    do {
        sleep(2);
        $sql = "SELECT * FROM connections where id=$id";
        $result = $conn->query($sql);
        $row = $result->fetch_assoc();
        if ($row["resAvailable"] == true) {
            $output = $row["res"];
        }
    } while ($row["resAvailable"] == false);


    //clear response available flag (request flag should be cleared but do it again)
    $sql = "UPDATE connections SET reqAvailable=false, resAvailable=false where id=$id";
    
    //print response
    echo $output;
}


?>