/*
   -------------------------------------------------------------------------------------
   readDataFromScale
   Arduino script to read data fro HX711 card.
   For Jade project by Chloé Devanne
   Written by Félix Cote
   -------------------------------------------------------------------------------------
*/

#include <HX711_ADC.h>

//pins:
const int HX711_dout = 4; //mcu > HX711 dout pin
const int HX711_sck = 5; //mcu > HX711 sck pin

//HX711 constructor:
HX711_ADC LoadCell(HX711_dout, HX711_sck);

// time interval
long t;

void setup() {
  // init serial port
  Serial.begin(57600); delay(10);
  //Serial.println();
  //Serial.println("Starting...");

  // setup HX711
  LoadCell.begin();
  float calibrationValue; 
  calibrationValue = 24.0;

  // load HX711 with calibration
  long stabilizingtime = 2000; // preciscion right after power-up can be improved by adding a few seconds of stabilizing time
  boolean _tare = true; // set to true only if nothing is on the board
  LoadCell.start(stabilizingtime, _tare);
  if (LoadCell.getTareTimeoutFlag()) {
    //Serial.println("Timeout, check MCU>HX711 wiring and pin designations");
    while (1);
  }
  else {
    LoadCell.setCalFactor(calibrationValue); // set calibration value (float)
    //Serial.println("Startup is complete");
  }
}

void loop() {
  static boolean newDataReady = 0;
  const int serialPrintInterval = 0; //increase value to slow down serial print activity

  // check for new data/start next conversion:
  if (LoadCell.update()) newDataReady = true;

  // get smoothed value from the dataset:
  if (newDataReady) {
    if (millis() > t + serialPrintInterval) {
      float i = LoadCell.getData();
      //Serial.print("Load_cell output val: ");
      Serial.println(i);
      newDataReady = 0;
      t = millis();
    }
  }
}
