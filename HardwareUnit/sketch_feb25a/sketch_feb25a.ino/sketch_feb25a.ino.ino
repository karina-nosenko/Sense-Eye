#include <DFRobotDFPlayerMini.h>

/***************************************************
DFPlayer - A Mini MP3 Player For Arduino
 <https://www.dfrobot.com/index.php?route=product/product&product_id=1121>

 ***************************************************
 This example shows the basic function of library for DFPlayer.

 Created 2016-12-07
 By [Angelo qiao](Angelo.qiao@dfrobot.com)

 GNU Lesser General Public License.
 See <http://www.gnu.org/licenses/> for details.
 All above must be included in any redistribution
 ****************************************************/

/***********Notice and Trouble shooting***************
 1.Connection and Diagram can be found here
 <https://www.dfrobot.com/wiki/index.php/DFPlayer_Mini_SKU:DFR0299#Connection_Diagram>
 2.This code is tested on Arduino Uno, Leonardo, Mega boards.
 ****************************************************/

#include "SoftwareSerial.h"
#include "DFRobotDFPlayerMini.h"

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
const char* ssid = "Redmi Note 9 Pro";
const char* password = "Aa123456789";
bool pressed = false;
int recommend;
// Set web server port number to 80
ESP8266WebServer server(80);
// Host
const char* host = "172.26.93.30";
WiFiClient client_to_server;
// Variable to store the HTTP request
String header;
const char input13 = 13; // the button GPIO16
// Current time
unsigned long currentTime = millis();
// Previous time
unsigned long previousTime = 0; 
// Define timeout time in milliseconds (example: 2000ms = 2s)
const long timeoutTime = 2000;
String url;

SoftwareSerial mySoftwareSerial(4, 5);  // RX, TX
DFRobotDFPlayerMini myDFPlayer;
void printDetail(uint8_t type, int value);

void setup() {
  mySoftwareSerial.begin(9600);
  Serial.begin(115200);
  Serial.println();
  Serial.println(F("DFRobot DFPlayer Mini Demo"));
  Serial.println(F("Initializing DFPlayer ... (May take 3~5 seconds)"));

  while (!myDFPlayer.begin(mySoftwareSerial)) {  //Use softwareSerial to communicate with mp3.
    Serial.println(F("Unable to begin:"));
    Serial.println(F("1.Please recheck the connection!"));
    Serial.println(F("2.Please insert the SD card!"));
  }
  Serial.println(F("DFPlayer Mini online."));

  pinMode(input13, INPUT_PULLUP);
  WiFi.begin(ssid, password);
   while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  // Print local IP address and start web server
  Serial.println("");
  Serial.println("WiFi connected.");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  delay(5000);
  Serial.print("connecting to ");
  Serial.println(host);
    // Use WiFiClient class to create TCP connections

  const int httpPort = 5000;
  // Connect to server
  if (client_to_server.connect(host, httpPort)) {
    Serial.println("Connected to server");
  } else {
    Serial.println("Connection to server failed");
  }
  // We now create a URI for the request
  url = "/save_id?color_band=orange&ip="+WiFi.localIP().toString();
  // Send request
  Serial.print("Requesting URL: ");
  Serial.println(url);
  
  client_to_server.print(String("GET ") + url + " HTTP/1.1\r\n" +
               "Host: " + host + "\r\n" + 
               "Connection: close\r\n\r\n");
  client_to_server.stop();
  delay(100);
  server.on("/recommend/move/0", move_0);
  server.on("/recommend/move/1", move_1);
  server.on("/recommend/move/2", move_2);
  server.on("/recommend/move/3", move_3);
  server.on("/recommend/move/4", move_4);
  server.on("/recommend/move/5", move_5);
  server.on("/recommend/move/6", move_6);
  server.on("/recommend/move/7", move_7);
  server.on("/recommend/move/8", move_8);
  server.on("/recommend/move/9", move_9);
  server.on("/recommend/move/10", move_10);
  server.on("/recommend/move/11", move_11);
  server.on("/recommend/move/12", move_12);
  server.on("/recommend/kick/1", kick_1);
  server.on("/recommend/kick/2", kick_2);
  server.on("/recommend/kick/3", kick_3);
  server.on("/recommend/kick/4", kick_4);
  server.on("/recommend/kick/5", kick_5);
  server.on("/recommend/kick/6", kick_6);
  server.on("/recommend/kick/7", kick_7);
  server.on("/recommend/kick/8", kick_8);
  server.on("/recommend/kick/9", kick_9);
  server.on("/recommend/kick/10", kick_10);
  server.on("/recommend/kick/11", kick_11);
  server.on("/recommend/kick/12", kick_12);
  server.on("/recommend/pass/1", pass_1);
  server.on("/recommend/pass/2", pass_2);
  server.on("/recommend/pass/3", pass_3);
  server.on("/recommend/pass/4", pass_4);
  server.on("/recommend/pass/5", pass_5);
  server.on("/recommend/pass/6", pass_6);
  server.on("/recommend/pass/7", pass_7);
  server.on("/recommend/pass/8", pass_8);
  server.on("/recommend/pass/9", pass_9);
  server.on("/recommend/pass/10", pass_10);
  server.on("/recommend/pass/11", pass_11);
  server.on("/recommend/pass/12", pass_12);
  server.begin();
}

void loop() {
  static unsigned long timer = millis();

  if (millis() - timer > 3000) {
    timer = millis();
  }

  if (myDFPlayer.available()) {
    printDetail(myDFPlayer.readType(), myDFPlayer.read());  //Print the detail message from DFPlayer to handle different errors and states.
  }

  server.handleClient();
  bool currentState = digitalRead(input13);
  if(currentState == pressed) {
    Serial.println("Hello");
    turn_recommended_sound();
    while(digitalRead(input13) == pressed) {
      // Do nothing
    }
  }
}

void kick_1() {
    recommend = 1;
    server.send(200, "text/html", "hello from esp8266!"); 
}

void kick_2() {
    recommend = 2;
    server.send(200, "text/html", "hello from esp8266!"); 
}

void kick_3() {
    recommend = 3;
    server.send(200, "text/html", "hello from esp8266!");    
}
void kick_4() {
    recommend = 4;
    server.send(200, "text/html", "hello from esp8266!");  
}
void kick_5() {
    recommend = 5;
    server.send(200, "text/html", "hello from esp8266!"); 
}
void kick_6() {
    recommend = 6;
    server.send(200, "text/html", "hello from esp8266!"); 
}
void kick_7() {
    recommend = 7;
    server.send(200, "text/html", "hello from esp8266!"); 
}
void kick_8() {
    recommend = 8;
    server.send(200, "text/html", "hello from esp8266!"); 
}
void kick_9() {
    recommend = 9;
    server.send(200, "text/html", "hello from esp8266!");  
}
void kick_10() {
    recommend = 10;
    server.send(200, "text/html", "hello from esp8266!"); 
}
void kick_11() {
    recommend = 11;
    server.send(200, "text/html", "hello from esp8266!");    
}
void kick_12() {
    recommend = 12;
    server.send(200, "text/html", "hello from esp8266!");  
}

void pass_1() {
    recommend = 13;
    server.send(200, "text/html", "hello from esp8266!"); 
}
void pass_2() {
    recommend = 14;
    server.send(200, "text/html", "hello from esp8266!");    
}
void pass_3() {
    recommend = 15;
    server.send(200, "text/html", "hello from esp8266!");   
}
void pass_4() {
    recommend = 16;
    server.send(200, "text/html", "hello from esp8266!");   
}
void pass_5() {
    recommend = 17;
    server.send(200, "text/html", "hello from esp8266!");   
}
void pass_6() {
    recommend = 18;
    server.send(200, "text/html", "hello from esp8266!");   
}
void pass_7() {
    recommend = 19;
    server.send(200, "text/html", "hello from esp8266!");    
}
void pass_8() {
    recommend = 20;
    server.send(200, "text/html", "hello from esp8266!");   
}
void pass_9() {
    recommend = 21;
    server.send(200, "text/html", "hello from esp8266!");    
}
void pass_10() {
    recommend = 22;
    server.send(200, "text/html", "hello from esp8266!");    
}
void pass_11() {
    recommend = 23;
    server.send(200, "text/html", "hello from esp8266!"); 
}
void pass_12() {
    recommend = 24;
    server.send(200, "text/html", "hello from esp8266!"); 
}
void move_0() {
    recommend = 37;
    server.send(200, "text/html", "hello from esp8266!"); 
}
void move_1() {
    recommend = 25;
    server.send(200, "text/html", "hello from esp8266!"); 
}

void move_2() {
    recommend = 26;
    server.send(200, "text/html", "hello from esp8266!"); 
}

void move_3() {
    recommend = 27;
    server.send(200, "text/html", "hello from esp8266!"); 
}

void move_4() {
    recommend = 28;
    server.send(200, "text/html", "hello from esp8266!"); 
}

void move_5() {
    recommend = 29;
    server.send(200, "text/html", "hello from esp8266!"); 
}

void move_6() {
    recommend = 30;
    server.send(200, "text/html", "hello from esp8266!"); 
}

void move_7() {
    recommend = 31;
    server.send(200, "text/html", "hello from esp8266!"); 
}

void move_8() {
    recommend = 32;
    server.send(200, "text/html", "hello from esp8266!"); 
}

void move_9() {
    recommend = 33;
    server.send(200, "text/html", "hello from esp8266!"); 
}

void move_10() {
    recommend = 34;
    server.send(200, "text/html", "hello from esp8266!"); 
}

void move_11() {
    recommend = 35;
    server.send(200, "text/html", "hello from esp8266!"); 
}

void move_12() {
    recommend = 36;
    server.send(200, "text/html", "hello from esp8266!"); 
}



//function output sound
void turn_recommended_sound() {
  myDFPlayer.volume(30);  //Set volume value. From 0 to 30
  myDFPlayer.play(recommend);     //Play the first mp3
  
}

void printDetail(uint8_t type, int value) {
  switch (type) {
    case TimeOut:
      Serial.println(F("Time Out!"));
      break;
    case WrongStack:
      Serial.println(F("Stack Wrong!"));
      break;
    case DFPlayerCardInserted:
      Serial.println(F("Card Inserted!"));
      break;
    case DFPlayerCardRemoved:
      Serial.println(F("Card Removed!"));
      break;
    case DFPlayerCardOnline:
      Serial.println(F("Card Online!"));
      break;
    case DFPlayerPlayFinished:
      Serial.print(F("Number:"));
      Serial.print(value);
      Serial.println(F(" Play Finished!"));
      break;
    case DFPlayerError:
      Serial.print(F("DFPlayerError:"));
      switch (value) {
        case Busy:
          Serial.println(F("Card not found"));
          break;
        case Sleeping:
          Serial.println(F("Sleeping"));
          break;
        case SerialWrongStack:
          Serial.println(F("Get Wrong Stack"));
          break;
        case CheckSumNotMatch:
          Serial.println(F("Check Sum Not Match"));
          break;
        case FileIndexOut:
          Serial.println(F("File Index Out of Bound"));
          break;
        case FileMismatch:
          Serial.println(F("Cannot Find File"));
          break;
        case Advertise:
          Serial.println(F("In Advertise"));
          break;
        default:
          break;
      }
      break;
    default:
      break;
  }
}