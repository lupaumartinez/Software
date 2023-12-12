
//Temperature sensor LM35

int sensorPin = A0;    // select the input pin 
float sensorValue = 0;  // variable to store the value coming from the sensor
float sensorTemp = 0.0; // variable temperature
int stepTime = 100;   // variable to delay the loop
int kp = -10; // proportinal factor of the PID
int dutyCycle = 0; // starts off
int analogPin = 3; // pin for transistor's gate
int numberOfPoints = 10; // number of temperature measurements to average
int i = 0; // counter
float correction; // correction factor for PID

float setPointTemperature = 20;

char incomingBytes = 0;
String readString = "";

void setup() {
  // config serial communication
  //Serial.begin(9600);
  Serial.begin(2000000);
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
      Serial.println((String)":dutyCycle:"+dutyCycle);
      readString="";
    } 
    else {
      Serial.print("Temperature setpoint was changed to: ");
      Serial.println((String)aux);
      setPointTemperature = aux;
      readString="";
    } 
  }
  
//  instruction = Serial.parseFloat();
//  
//  if (instruction == 999) {
//    Serial.print((String)"setpoint: "+setPointTemperature);
//    Serial.print((String)" -- sensorTemp: "+sensorTemp);
//    Serial.println((String)" -- dutyCycle: "+dutyCycle);
//    instruction = -1;
//  }
//  else if (instruction == 20) {
//    Serial.println((String)"Setpoint was changed.");
//    setPointTemperature = instruction;
//    instruction = -1;
//  }
  
  // read the value from the sensor LM35
  sensorValue = 0;
  for (i = 0; i < numberOfPoints; i++) {
    sensorValue = sensorValue + analogRead(sensorPin);
  }
  sensorValue = sensorValue/numberOfPoints;
  
  sensorTemp = ((5.0 * sensorValue) / 1023.0) * 100.0;  //conversion of temp to Celsius
  //  Serial.println(sensorTemp);
  
  // PID
  correction = kp*(sensorTemp - setPointTemperature);
  dutyCycle = dutyCycle + (int)correction;
  
  // keep dutyCycle value inside allowed range
  if (dutyCycle > 255) {
    dutyCycle = 255;
  }
  if (dutyCycle < 0) {
    dutyCycle = 0;
  }

  analogWrite(analogPin, dutyCycle); 
  
  delay(stepTime);
}
