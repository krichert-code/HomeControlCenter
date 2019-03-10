#include "etherShield.h"
#include "ETHER_28J60.h"
#include <avr/wdt.h> //should be in any adruino IDE


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

static uint8_t mac[6] = {0x54, 0x55, 0x58, 0x10, 0x00, 0x24};   
static uint8_t ip[4] = {192, 168, 1, 2};                       
static uint16_t port = 80;                                     
static uint8_t status;
static unsigned long httpTime = 0;
static unsigned long currentTime = 0;

ETHER_28J60 e;
void(* resetFunc) (void) = 0; //declare reset function @ address 0

void setup()
{  
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
    
     e.setup(mac, ip, port);
     wdt_enable(WDTO_8S); //enable it, and set it to 8s
     
     //only for debug purpose
#ifdef DEBUG     
     Serial.begin(9600);      // open the serial port at 9600 bps:
     Serial.println("Debug");
#endif     
 }
 
 void loop()
 {
   char* params;
   int   in;
   
        
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
#ifdef DEBUG        
      Serial.println("disable");
#endif         
   }
   //-------------------------------------------------------------------------   
       
   /* read http request and create response*/   
   //-------------------------------------------------------------------------
   params = e.serviceRequest();
   
   if (params != NULL)
   {
     //get timestamp - used to perform reset if http request cannot be handled
     httpTime = millis();
     
     if (strcmp(params, "gate0") == 0)
     {
       e.print("OK");          
       e.respond();           
       digitalWrite(GATE,HIGH);
       delay(500);
       digitalWrite(GATE,LOW);
     }
     else if (strcmp(params, "gate1") == 0)
     {
       e.print("OK");          
       e.respond();           
       digitalWrite(GATE1,HIGH);
       delay(500);
       digitalWrite(GATE1,LOW);
     }
     else if (strcmp(params, "door") == 0)
     {    
       e.print("OK");          
       e.respond();           
       digitalWrite(DOOR,HIGH);
       delay(2000);
       digitalWrite(DOOR,LOW);
     }
     else if (strcmp(params, "heat_on") == 0)
     {    
       e.print("OK");          
       e.respond();           
       digitalWrite(HEAT,HIGH);
       status = status | (1 << (HEAT-OFFSET));
     }
     else if (strcmp(params, "heat_off") == 0)
     {    
       e.print("OK");          
       e.respond();           
       digitalWrite(HEAT,LOW);
       status = status & (~(1 << (HEAT-OFFSET)));
     }
     else if (strcmp(params, "water1_on") == 0)
     {    
       e.print("OK");          
       e.respond();           
       digitalWrite(WATER1,HIGH);
       digitalWrite(WATER2,LOW);
       digitalWrite(WATER3,LOW); 
       digitalWrite(TRAFO, HIGH);       
       status = status | (1 << (WATER1-OFFSET));       
       status = status & (~(1 << (WATER2-OFFSET)));       
       status = status & (~(1 << (WATER3-OFFSET)));              
     }
     else if (strcmp(params, "water2_on") == 0)
     {    
       e.print("OK");          
       e.respond();           
       digitalWrite(WATER1,LOW);
       digitalWrite(WATER2,HIGH);
       digitalWrite(WATER3,LOW); 
       digitalWrite(TRAFO, HIGH);       
       status = status | (1 << (WATER2-OFFSET));       
       status = status & (~(1 << (WATER1-OFFSET)));       
       status = status & (~(1 << (WATER3-OFFSET)));              
     }
     else if (strcmp(params, "water3_on") == 0)
     {    
       e.print("OK");          
       e.respond();           
       digitalWrite(WATER1,LOW);
       digitalWrite(WATER2,LOW);
       digitalWrite(WATER3,HIGH);  
       digitalWrite(TRAFO, HIGH);
       status = status | (1 << (WATER3-OFFSET));       
       status = status & (~(1 << (WATER2-OFFSET)));       
       status = status & (~(1 << (WATER1-OFFSET)));              
     }
     else if (strcmp(params, "water_off") == 0)
     {    
       e.print("OK");          
       e.respond();           
       digitalWrite(WATER1,LOW);
       digitalWrite(WATER2,LOW);
       digitalWrite(WATER3,LOW);       
       digitalWrite(TRAFO, LOW);
       status = status & (~(1 << (WATER1-OFFSET)));       
       status = status & (~(1 << (WATER2-OFFSET)));       
       status = status & (~(1 << (WATER3-OFFSET)));              
     }     
     else if (strcmp(params, "status") == 0)
     {    
       e.print(status);          
       e.respond();           
     }          
   }
   //-------------------------------------------------------------------------
   
   //watchdog handling
   //-------------------------------------------------------------------------
   currentTime = millis();
   
   //timer overlap - reset timer
   if (currentTime-httpTime < 0 )
   {
      httpTime = millis();
      currentTime = millis();
   }
   
   //on each 30min should appear at least on http request else reset system
   if (currentTime-httpTime > 1000*60*30)
   {
     //call NULL function - dirty trick
     resetFunc();
   }   
   
   //reset watchdog - it prevents to infinity loop
   wdt_reset();
   //-------------------------------------------------------------------------   
 }
 
  
