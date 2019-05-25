#include <ArduinoJson.h>
#include <math.h>

const int FSR_PIN[16] = {A0, A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11, A12, A13, A14, A15};

int trigPin1=22;
int echoPin1=24;
int trigPin2=26;
int echoPin2=28;

void setup() {
 // put your setup code here, to run once:s
 Serial.begin(9600);

 for(int i=0;i<16;i++){
     pinMode(FSR_PIN[i], INPUT);
 }
 pinMode(trigPin1, OUTPUT);
 pinMode(echoPin1, INPUT);
 pinMode(trigPin2, OUTPUT);
 pinMode(echoPin2, INPUT);
}

void loop() {
 // put your main code here, to run repeatedly:
 StaticJsonBuffer<200> jsonBuffer;
 JsonObject& sensors = jsonBuffer.createObject();


 sensors["user"] = "Haeyoon";
 //pressure["timestamp"] = local;
 JsonArray& data1 = sensors.createNestedArray("pressure");
 JsonArray& data2 = sensors.createNestedArray("ultra");

 /*capturing the pressure sensor values*/
 for(int i=0;i<16;i++){
   int value = analogRead(FSR_PIN[i]);
   //data1.add(map(value, 0, 1000, 255, 0));
   data1.add(value);
 }
 /*capturing the ultrasonic sensor values*/
 long duration1, distance1, duration2, distance2;
 digitalWrite(trigPin1, LOW);
 delayMicroseconds(2);
 digitalWrite(trigPin1, HIGH);
 delayMicroseconds(10);
 digitalWrite(trigPin1, LOW);
 duration1 = pulseIn(echoPin1, HIGH);
 distance1 = (duration1/2) /29.1;

 if(distance1 >=400 || distance1 <=0){
   //data2.add("Invalid");
   data1.add(-1);
  }
 else{
   //data2.add(distance1); //in centimeter
   data1.add(distance1);
  }

  digitalWrite(trigPin2, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin2, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin2, LOW);
  duration2 = pulseIn(echoPin2, HIGH);
  distance2= (duration2/2) / 29.1;

   if (distance2 >= 400 || distance2 <= 0){
    //data2.add("Invalid");
    data1.add(-1);
  }
  else {
    //data2.add(distance2);
    data1.add(distance2);
  }

 sensors.printTo(Serial);
 Serial.println(",");

 delay(1000);
}
