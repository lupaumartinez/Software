
//Temperature sensor LM35

int sensorPin = A0;    // select the input pin 
int sensorValue = 0;  // variable to store the value coming from the sensor
float sensorTemp = 0.0; // variable temperature
int step_time = 100;   // variable to delay the loop

void setup() {
  // initialize serial communications:
  Serial.begin(9600);
}

void loop() {
  // read the value from the sensor LM35:
  sensorValue = analogRead(sensorPin);
  sensorTemp = ((5.0 * sensorValue) / 1024) * 100.0;  //conversion to temp Celsius
  Serial.println(sensorTemp);
  delay(step_time);
}
