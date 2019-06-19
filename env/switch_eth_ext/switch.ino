/* For test purpose connect PC directly to switch using ethernet cable*/

#include <EtherCard.h>
#include <avr/wdt.h>

#define TCP_FLAGS_FIN_V 1 //as declared in net.h
#define TCP_FLAGS_ACK_V 0x10 //as declared in net.h

#define TRAFO        A0
#define GATE         9
#define HEAT         8
#define DOOR         7
#define GATE1        6
#define WATER1       5
#define WATER2       4
#define WATER3       3
#define AUX          2
#define OFFSET       2

//#define DEBUG

static byte mymac[] = {0x54, 0x55, 0x58, 0x10, 0x00, 0x24};   
static byte myip[] = { 192,168,1,2 };
byte Ethernet::buffer[900]; // tcp ip send and receive buffer
static uint8_t status;
BufferFiller bfill;

//time without http request (1000*60 * minues)
static unsigned long  maxIntervalWihoutHttpReq = 1000L *60 * 2; //2min
static unsigned long  httpTime = 0;
static unsigned long  currentTime = 0;


const char responseOK[] PROGMEM =
"HTTP/1.0 200 OK\r\n"
"Content-Type: text/html\r\n"
"\r\n"
"OK"
;

const char responseStatus[] PROGMEM =
"HTTP/1.0 200 OK\r\n"
"Content-Type: text/html\r\n"
"\r\n"
"$D"
;

const char infoPage[] PROGMEM =
"HTTP/1.0 200 OK\r\n"
"Content-Type: text/html\r\n"
"\r\n"
"<html>"
  "<head><title>"
    "multipackets Test"
  "</title></head>"
  "<body>"
    "<p><em>"
      "Request not supported"
      "<br><br>"
      "<b>GET /status</b>  - return current status of devices<br>"
      "<b>GET /water1_on</b>  - enable sprinklers from zone 1<br>"
      "<b>GET /water2_on</b>  - enable sprinklers from zone 2<br>"
      "<b>GET /water3_on</b>  - enable sprinklers from zone 3<br>"
      "<b>GET /water_off</b>  - disable sprinklers<br>"
      "<b>GET /gate0</b>  - open gate 0<br>"      
      "<b>GET /gate1</b>  - open gate 1<br>"            
      "<b>GET /door</b>   - open door<br>"                  
      "<b>GET /heat_on</b>  - enable heater<br>"      
      "<b>GET /heat_off</b>  - disable heater<br>"            
    "</em></p>"
;

void(* resetFunc) (void) = 0; //declare reset function @ address 0

void setup(){
     wdt_disable(); //always good to disable it, if it was left 'on' or you need init time
     delay(500);
   
     pinMode(GATE, OUTPUT);
     pinMode(GATE1, OUTPUT);
     pinMode(HEAT, OUTPUT);
     pinMode(DOOR, OUTPUT);
     pinMode(WATER1, OUTPUT);
     pinMode(WATER2, OUTPUT);
     pinMode(WATER3, OUTPUT);
     pinMode(AUX, INPUT);
     pinMode(TRAFO, OUTPUT);
    
     digitalWrite(GATE,LOW);
     digitalWrite(GATE1, LOW);
     digitalWrite(HEAT, LOW);
     digitalWrite(DOOR, LOW);
     digitalWrite(WATER1, LOW);
     digitalWrite(WATER2, LOW);
     digitalWrite(WATER3, LOW);
     digitalWrite(AUX, HIGH);
     digitalWrite(TRAFO, LOW);
    
     //only for debug purpose
#ifdef DEBUG     
     Serial.begin(9600);      // open the serial port at 9600 bps:
     Serial.println("Debug");
#endif     

     wdt_enable(WDTO_8S); //enable it, and set it to 8s

  // Change 'SS' to your Slave Select pin, if you arn't using the default pin
  ether.begin(sizeof Ethernet::buffer, mymac , SS);
  ether.staticSetup(myip, NULL);
}


void loop(){
    word pos = ether.packetLoop(ether.packetReceive());
    int   in;
    unsigned long timeDiff = 0;
    
   /* read input and update status */
   //-------------------------------------------------------------------------   
   in = digitalRead(AUX);
   if (in == LOW)
   {
     status = status | (1 << (AUX-OFFSET));       
#ifdef DEBUG        
     Serial.println("enable");
#endif   
   }
   else
   {     
      status = status & (~(1 << (AUX-OFFSET)));       
   }
   //-------------------------------------------------------------------------   
    
    // check if valid tcp data is received
    if (pos) {
       //get timestamp - used to perform reset if http request cannot be handled
        httpTime = millis();
      
        char* data = (char *) Ethernet::buffer + pos;

        if (strncmp("GET /gate0", data, 10) == 0) 
        {
            ether.httpServerReplyAck(); // send ack to the request            
            memcpy_P(ether.tcpOffset(), responseOK, sizeof responseOK);//only the first part will sended
            ether.httpServerReply_with_flags(sizeof responseOK - 1,TCP_FLAGS_ACK_V|TCP_FLAGS_FIN_V);
            digitalWrite(GATE,HIGH);
            delay(500);
            digitalWrite(GATE,LOW);
        }
        else if (strncmp("GET /gate1", data, 10) == 0) 
        {
            ether.httpServerReplyAck(); // send ack to the request            
            memcpy_P(ether.tcpOffset(), responseOK, sizeof responseOK);//only the first part will sended
            ether.httpServerReply_with_flags(sizeof responseOK - 1,TCP_FLAGS_ACK_V|TCP_FLAGS_FIN_V);
            digitalWrite(GATE1,HIGH);
            delay(500);
            digitalWrite(GATE1,LOW);
        }
        else if (strncmp("GET /door", data, 9) == 0) 
        {
            ether.httpServerReplyAck(); // send ack to the request            
            memcpy_P(ether.tcpOffset(), responseOK, sizeof responseOK);//only the first part will sended
            ether.httpServerReply_with_flags(sizeof responseOK - 1,TCP_FLAGS_ACK_V|TCP_FLAGS_FIN_V);
            digitalWrite(DOOR,HIGH);
            delay(500);
            digitalWrite(DOOR,LOW);
     }
     else if (strncmp("GET /heat_on", data, 12) == 0) 
     {
            ether.httpServerReplyAck(); // send ack to the request            
            memcpy_P(ether.tcpOffset(), responseOK, sizeof responseOK);//only the first part will sended
            ether.httpServerReply_with_flags(sizeof responseOK - 1,TCP_FLAGS_ACK_V|TCP_FLAGS_FIN_V);
            digitalWrite(HEAT,HIGH);
            status = status | (1 << (HEAT-OFFSET));
     }
     else if (strncmp("GET /heat_off", data, 13) == 0) 
     {
            ether.httpServerReplyAck(); // send ack to the request            
            memcpy_P(ether.tcpOffset(), responseOK, sizeof responseOK);//only the first part will sended
            ether.httpServerReply_with_flags(sizeof responseOK - 1,TCP_FLAGS_ACK_V|TCP_FLAGS_FIN_V);
            digitalWrite(HEAT,LOW);
            status = status & (~(1 << (HEAT-OFFSET)));
     }     
     else if (strncmp("GET /water1_on", data, 14) == 0) 
     {
            ether.httpServerReplyAck(); // send ack to the request            
            memcpy_P(ether.tcpOffset(), responseOK, sizeof responseOK);//only the first part will sended
            ether.httpServerReply_with_flags(sizeof responseOK - 1,TCP_FLAGS_ACK_V|TCP_FLAGS_FIN_V);
            digitalWrite(WATER1,HIGH);
            digitalWrite(WATER2,LOW);
            digitalWrite(WATER3,LOW); 
            digitalWrite(TRAFO, HIGH);       
            status = status | (1 << (WATER1-OFFSET));       
            status = status & (~(1 << (WATER2-OFFSET)));       
            status = status & (~(1 << (WATER3-OFFSET)));                          
      }
      else if (strncmp("GET /water2_on", data, 14) == 0) 
      {
           ether.httpServerReplyAck(); // send ack to the request            
           memcpy_P(ether.tcpOffset(), responseOK, sizeof responseOK);//only the first part will sended
           ether.httpServerReply_with_flags(sizeof responseOK - 1,TCP_FLAGS_ACK_V|TCP_FLAGS_FIN_V);
           digitalWrite(WATER1,LOW);
           digitalWrite(WATER2,HIGH);
           digitalWrite(WATER3,LOW); 
           digitalWrite(TRAFO, HIGH);       
           status = status | (1 << (WATER2-OFFSET));       
           status = status & (~(1 << (WATER1-OFFSET)));       
           status = status & (~(1 << (WATER3-OFFSET)));              
      }
      else if (strncmp("GET /water3_on", data, 14) == 0) 
      {
            ether.httpServerReplyAck(); // send ack to the request            
            memcpy_P(ether.tcpOffset(), responseOK, sizeof responseOK);//only the first part will sended
            ether.httpServerReply_with_flags(sizeof responseOK - 1,TCP_FLAGS_ACK_V|TCP_FLAGS_FIN_V);
            digitalWrite(WATER1,LOW);
            digitalWrite(WATER2,LOW);
            digitalWrite(WATER3,HIGH);  
            digitalWrite(TRAFO, HIGH);
            status = status | (1 << (WATER3-OFFSET));       
            status = status & (~(1 << (WATER2-OFFSET)));       
            status = status & (~(1 << (WATER1-OFFSET)));              
       }        
       else if (strncmp("GET /water_off", data, 14) == 0) 
       {
            ether.httpServerReplyAck(); // send ack to the request            
            memcpy_P(ether.tcpOffset(), responseOK, sizeof responseOK);//only the first part will sended
            ether.httpServerReply_with_flags(sizeof responseOK - 1,TCP_FLAGS_ACK_V|TCP_FLAGS_FIN_V);
            digitalWrite(WATER1,LOW);
            digitalWrite(WATER2,LOW);
            digitalWrite(WATER3,LOW);  
            digitalWrite(TRAFO, LOW);
            status = status & (~(1 << (WATER3-OFFSET)));       
            status = status & (~(1 << (WATER2-OFFSET)));       
            status = status & (~(1 << (WATER1-OFFSET)));              
        }        
        else if (strncmp("GET /status", data, 11) == 0) 
        {
          ether.httpServerReplyAck(); // send ack to the request
          bfill = ether.tcpOffset();
          bfill.emit_p(responseStatus, status);          
          ether.httpServerReply_with_flags(bfill.position(),TCP_FLAGS_ACK_V|TCP_FLAGS_FIN_V);
        }
        else
        {
           ether.httpServerReplyAck(); // send ack to the request
           memcpy_P(ether.tcpOffset(), infoPage, sizeof infoPage); // send fiveth packet and send the terminate flag
           ether.httpServerReply_with_flags(sizeof infoPage - 1,TCP_FLAGS_ACK_V|TCP_FLAGS_FIN_V); 
        }
        
   //watchdog handling
   //-------------------------------------------------------------------------
   currentTime = millis();

   //timer overlap - reset timer
   if (currentTime < httpTime)
   {
      httpTime = millis();
      currentTime = millis();
   }

   timeDiff = currentTime-httpTime;    
  }
  
   delay(100);    
  
   if (timeDiff > maxIntervalWihoutHttpReq)
   {
#ifdef DEBUG        
     Serial.println("--RESET--");
     delay(20000);
     Serial.println("--WD RESET DOESN'T OCCUR, DO IT MANUALLY--");
#endif           
     //call NULL function - dirty trick
     resetFunc();
    }   
  
   //reset watchdog - it prevents to infinity loop
   wdt_reset();     
}
