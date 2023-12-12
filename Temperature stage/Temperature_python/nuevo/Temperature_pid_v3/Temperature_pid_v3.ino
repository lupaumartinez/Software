
//Temperature sensor LM35

int sensorPin = A0;    // select the input pin 
float sensorValue = 0;  // variable to store the value coming from the sensor
float sensorTemp = 0.0; // variable temperature
int numberOfPoints = 16; // number of temperature measurements to average
int analogPin = 3; // pin for transistor's gate
int i = 0; // counter

char incomingBytes = 0; // byte to read from serial port
String readString = ""; // string received from serial port

int dutyCycle = 0; // starts off
float setPointTemperature = 20; // starting temp setpoint

float error = 0; // PID error term
float lastError = 0; // PID last error term
float propCorrection = 0; // correction factor for Proportional PID term 
float intCorrection = 0; // correction factor for Integral PID term 
float devCorrection = 0; // correction factor for Derivative PID term 

int stepTime = 10; // variable to delay the loop

float kp = -100; // proportinal factor of the PID
float ki = -0.0001; // integral factor of the PID
float kd = 4500; // derivative factor of the PID

void setup() {
  // config serial communication
  Serial.begin(2000000);
  // transistor's gate pin
  pinMode(analogPin, OUTPUT);
}

void loop() {
  
  // read the incoming bytes
  while (Serial.available() > 0) {
    char incomingBytes = Serial.read();
    readString += incomingBytes;
  }
  
  // notify if readString is non-zero
  if (readString.length() > 0) {
    float aux = readString.toFloat();
    if (aux == 0) {
      Serial.print((String)"setpoint:"+setPointTemperature);
      Serial.print((String)":sensorTemp:"+sensorTemp);
      Serial.print((String)":dutyCycle:"+dutyCycle);
      Serial.print((String)":error:"+error);
      Serial.print((String)":propTerm:"+propCorrection);
      Serial.print((String)":intTerm:"+intCorrection);
      Serial.println((String)":devTerm:"+devCorrection);
      readString="";
    }
//    else if (aux == 1) {
//        Serial.println((String)"--------------");
//        Serial.println((String)"Error "+error);
//        Serial.println((String)"Prop term "+propCorrection);
//        Serial.println((String)"Int term "+intCorrection);
//        Serial.println((String)"Dev term "+devCorrection);
//        Serial.println((String)"duty "+dutyCycle);
//        readString="";
//    }
    else {
      Serial.print("Temperature setpoint was changed to: ");
      Serial.println((String)aux);
      setPointTemperature = aux;
      readString="";
      intCorrection = 0;
    } 
  }
  
  // read the value from the sensor LM35
  sensorValue = 0;
  for (i = 0; i < numberOfPoints; i++) {
    sensorValue = sensorValue + analogRead(sensorPin);
  }
  sensorValue = sensorValue/numberOfPoints;
  
  sensorTemp = ((5.0 * sensorValue) / 1023.0) * 100.0;  //conversion of temp to Celsius
  
  // PID
  error = sensorTemp - setPointTemperature;
  
  // proportional term
  propCorrection = kp*error;

  // integral term
  intCorrection += ki*error*stepTime;

  // derivative term
  devCorrection = kd*(error - lastError)/stepTime;
  lastError = error;
  
  // process variable
  dutyCycle = (int) propCorrection + (int) intCorrection ;//+ (int) devCorrection;
  
  // keep dutyCycle value inside the allowed range
  if (dutyCycle > 255) {
    dutyCycle = 255;
  }
  if (dutyCycle < 0) {
    dutyCycle = 0;
  }

  // update gate status
  analogWrite(analogPin, dutyCycle); 

  delay(stepTime);
}
