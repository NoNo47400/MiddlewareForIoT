#include <Arduino.h>
#include <ArduinoMqttClient.h>
#include <ESP8266WiFi.h>

int button_pin = 12;

char ssid[] = "asni";    // your network SSID (name)
char pass[] = "asniasni";    // your network password (use for WPA, or use as key for WEP)
WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);
const char broker[] = "10.0.1.254";
int        port     = 1883;
const char topic_led[]  = "state_led";
const char topic_button[]  = "Mikasa";
int previous_button_state = 0;
void setup() {
  // put your setup code here, to run once:
  //Initialize serial and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  pinMode(BUILTIN_LED, OUTPUT);
  pinMode(button_pin, INPUT);
  // attempt to connect to WiFi network:
  Serial.print("Attempting to connect to WPA SSID: ");
  Serial.println(ssid);
  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    // failed, retry
    Serial.print(".");
    delay(5000);
  }
  Serial.println("You're connected to the network");
  Serial.println();
  // You can provide a unique client ID, if not set the library uses Arduino-millis()
  // Each client must have a unique client ID
  // mqttClient.setId("clientId");
  // You can provide a username and password for authentication
  // mqttClient.setUsernamePassword("username", "password");
  Serial.print("Attempting to connect to the MQTT broker: ");
  Serial.println(broker);
  if (!mqttClient.connect(broker, port)) {
    Serial.print("MQTT connection failed! Error code = ");
    Serial.println(mqttClient.connectError());
    while (1);
  }
  Serial.println("You're connected to the MQTT broker!");
  Serial.println();
  Serial.print("Subscribing to topic: ");
  Serial.println(topic_led);
  Serial.println();
  // subscribe to a topic
  mqttClient.subscribe(topic_led);
  // topics can be unsubscribed using:
  // mqttClient.unsubscribe(topic);
  Serial.print("Waiting for messages on topic: ");
  Serial.println(topic_led);
  Serial.println();
  
}

void change_state_led(int state)
{
    Serial.print("State changed to ");
    Serial.println(state);
    digitalWrite(BUILTIN_LED, state);
}

void publish(const String& topic, int message) {
    mqttClient.beginMessage(topic);
    mqttClient.print(message);
    mqttClient.endMessage();
}

void loop() {
  int messageSize = mqttClient.parseMessage();
  if (messageSize && mqttClient.messageTopic()==topic_led) {
    // we received a message, print out the topic and contents
    Serial.print("Received a message with topic '");
    Serial.print(mqttClient.messageTopic());
    Serial.print("', length ");
    Serial.print(messageSize);
    Serial.print(" bytes:");
    // use the Stream interface to print the contents
    int message = (char)mqttClient.read()-'0';
    Serial.println(message);
    change_state_led(message);
    Serial.println();
    Serial.println();
  }
  int buttonState = digitalRead(button_pin);
  delay(10);
  if(buttonState!=previous_button_state) {
    publish(topic_button, !buttonState);

    previous_button_state=buttonState;
  }
}