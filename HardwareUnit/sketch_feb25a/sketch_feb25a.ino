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

////////////////////////////////////////
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
const char* ssid     = "Yuval";
const char* password = "Panama507";
bool pressed = false;
int recommended_index;

// Set web server port number to 80
ESP8266WebServer server(80);
// Host
const char* host = "192.168.14.3";
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

////////////////////////////////////////
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

  // myDFPlayer.volume(30);  //Set volume value. From 0 to 30
  // myDFPlayer.play(1);     //Play the first mp3
    ////////////////////////////////////////////////
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
  url = "/save_id?color_band=red&ip="+WiFi.localIP().toString();
  // Send request
  Serial.print("Requesting URL: ");
  Serial.println(url);
  
  client_to_server.print(String("GET ") + url + " HTTP/1.1\r\n" +
               "Host: " + host + "\r\n" + 
               "Connection: close\r\n\r\n");
  client_to_server.stop();
  delay(100);
  server.on("/recommend/1", handle_1);
  server.on("/recommend/2", handle_2);
  server.on("/recommend/3", handle_3);
  server.on("/recommend/4", handle_4);
  server.on("/recommend/5", handle_5);
  server.on("/recommend/6", handle_6);
  server.on("/recommend/7", handle_7);
  server.on("/recommend/8", handle_8);
  server.on("/recommend/9", handle_9);
  server.on("/recommend/10", handle_10);
  server.on("/recommend/11", handle_11);
  server.on("/recommend/12", handle_12);
  server.begin();
  ////////////////////////////////////////////
}

void loop() {
  static unsigned long timer = millis();

  if (millis() - timer > 3000) {
    timer = millis();
    //myDFPlayer.next();  //Play next mp3 every 3 second.
  }

  if (myDFPlayer.available()) {
    printDetail(myDFPlayer.readType(), myDFPlayer.read());  //Print the detail message from DFPlayer to handle different errors and states.
  }

  /////////////////////
  server.handleClient();
  bool currentState = digitalRead(input13);
  if(currentState == pressed) {
    Serial.println("Hello");
    turn_recommended_sound();
    while(digitalRead(input13) == pressed) {
      // Do nothing
    }
  }
  /////////////////////
}

void handle_1() {
    recommended_index = 1;
    server.send(200, "text/html", "hello from esp8266!"); 
    // output0State = "on";
    // digitalWrite(output0, HIGH);
    // delay(1000);
    // output5State = "off";
    // digitalWrite(output0, LOW);
}

void handle_2() {
    recommended_index = 2;
    server.send(200, "text/html", "hello from esp8266!"); 
    // output0State = "on";
    // digitalWrite(output0, HIGH);
    // delay(1000);
    // output5State = "off";
    // digitalWrite(output0, LOW);
}

void handle_3() {
    recommended_index = 3;
    server.send(200, "text/html", "hello from esp8266!"); 
    // output0State = "on";
    // digitalWrite(output0, HIGH);
    // delay(1000);
    // output5State = "off";
    // digitalWrite(output0, LOW);
}

void handle_4() {
    recommended_index = 4;
    server.send(200, "text/html", "hello from esp8266!"); 
    // output0State = "on";
    // digitalWrite(output0, HIGH);
    // delay(1000);
    // output5State = "off";
    // digitalWrite(output0, LOW);
}

void handle_5() {
    recommended_index = 5;
    server.send(200, "text/html", "hello from esp8266!"); 
    // output0State = "on";
    // digitalWrite(output0, HIGH);
    // delay(1000);
    // output5State = "off";
    // digitalWrite(output0, LOW);
}

void handle_6() {
    recommended_index = 6;
    server.send(200, "text/html", "hello from esp8266!"); 
    // output0State = "on";
    // digitalWrite(output0, HIGH);
    // delay(1000);
    // output5State = "off";
    // digitalWrite(output0, LOW);
}

void handle_7() {
    recommended_index = 7;
    server.send(200, "text/html", "hello from esp8266!"); 
    // output0State = "on";
    // digitalWrite(output0, HIGH);
    // delay(1000);
    // output5State = "off";
    // digitalWrite(output0, LOW);
}

void handle_8() {
    recommended_index = 8;
    server.send(200, "text/html", "hello from esp8266!"); 
    // output0State = "on";
    // digitalWrite(output0, HIGH);
    // delay(1000);
    // output5State = "off";
    // digitalWrite(output0, LOW);
}

void handle_9() {
    recommended_index = 9;
    server.send(200, "text/html", "hello from esp8266!"); 
    // output0State = "on";
    // digitalWrite(output0, HIGH);
    // delay(1000);
    // output5State = "off";
    // digitalWrite(output0, LOW);
}

void handle_10() {
    recommended_index = 10;
    server.send(200, "text/html", "hello from esp8266!"); 
    // output0State = "on";
    // digitalWrite(output0, HIGH);
    // delay(1000);
    // output5State = "off";
    // digitalWrite(output0, LOW);
}

void handle_11() {
    recommended_index = 11;
    server.send(200, "text/html", "hello from esp8266!"); 
    // output0State = "on";
    // digitalWrite(output0, HIGH);
    // delay(1000);
    // output5State = "off";
    // digitalWrite(output0, LOW);
}

void handle_12() {
    recommended_index = 12;
    server.send(200, "text/html", "hello from esp8266!"); 
    // output0State = "on";
    // digitalWrite(output0, HIGH);
    // delay(1000);
    // output5State = "off";
    // digitalWrite(output0, LOW);
}


//function output sound
void turn_recommended_sound() {
  myDFPlayer.volume(30);  //Set volume value. From 0 to 30
  myDFPlayer.play(recommended_index);     //Play the first mp3
  
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