/*
   -------------------------------------------------------------------------------------
   readDataFromScale
   Arduino script to read data fro HX711 card.
   For Jade project by Chloé Devanne
   Written by Félix Cote
   -------------------------------------------------------------------------------------
*/

#include <HX711.h>

//pins:
const int HX711_dout = 5; //mcu > HX711 dout pin
const int HX711_sck = 4; //mcu > HX711 sck pin

//HX711 constructor:
HX711 loadCell;

// time interval
long t;

void setup() {
  // init serial port
  Serial.begin(57600);
  
  // setup HX711
  loadCell.begin(HX711_dout, HX711_sck);
}

void loop() {
  //
  float val = loadCell.read_average(2);
  Serial.println(val);
}
