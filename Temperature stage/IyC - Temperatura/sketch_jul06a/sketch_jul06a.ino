
//Temperature sensor LM35

int step_time = 100;   // variable to delay the loop

// float setPointTemperature = 23;


void setup() {
  // initialize serial communications:
  Serial.begin(9600);
}

void loop()  {
  // send data only when you receive data:
  if (Serial.available() > 0) {

        float setPointTemperature = Serial.parseFloat();
        Serial.println(setPointTemperature);
      
        delay(step_time);
    }    
}
