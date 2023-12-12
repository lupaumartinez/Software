
//Temperature sensor LM35

int sensorPin = A0;    // select the input pin 
float sensorValue = 0;  // variable to store the value coming from the sensor
float sensorTemp = 0.0; // variable temperature
int step_time = 50;   // variable to delay the loop
int kp = -1;
int dutyCycle = 255; //Arranca apagado
int analogPin = 3; // 
int ventana = 5;
int i = 0;
float correction;

float setPointTemperature = 23;

void setup() {
  // initialize serial communications:
  Serial.begin(9600);
  pinMode(analogPin, OUTPUT);
}

void loop()  {
  // send data only when you receive data:
  
     // while (Serial.available() > 0) {

      setPointTemperature = Serial.parseFloat();
  // read the value from the sensor LM35:
 
      sensorValue = 0 ;
    
      for (i = 0; i<ventana; i++) {
        sensorValue = sensorValue + analogRead(sensorPin);
      }
      sensorValue = sensorValue/ventana;
      
      sensorTemp = ((5.0 * sensorValue) / 1023.0) * 100.0;  //conversion to temp Celsius
    //  Serial.println(sensorTemp);
    
      correction = kp*(sensorTemp - setPointTemperature);
      dutyCycle = dutyCycle + (int)correction;
    
      if (dutyCycle > 255) {
        dutyCycle = 255;
      }
    
      if (dutyCycle < 0) {
        dutyCycle = 0;
      }
      
      Serial.println((String)"x:"+sensorTemp+":y:"+dutyCycle);
      
      analogWrite(analogPin, dutyCycle); 
    
      delay(step_time);
}
