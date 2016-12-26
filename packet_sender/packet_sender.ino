#include "test.h"
SensorData data;
struct Status_t sts;

void writeDebug(unsigned long t)
{
  Serial.write(0xAA);
  Serial.write(0x55);
  Serial.write(0x00);

  //Serial.write(0x05);
  char buf [10];
  //unsigned long aaa = 10000;
  sprintf(buf, "%lu", t);
  uint8_t len = strlen(buf);
  Serial.write(len);
  Serial.println(buf);
}

#define DBGLEN 100
void writeDebug(char * const text)
{
  //Start bytes and 0x00 debug packet id
  Serial.write(0xAA);
  Serial.write(0x55);
  Serial.write(0x00);

  //Write length of text and text
  Serial.write(strlen(text));
  Serial.println(text);
}

void writeStruct(uint8_t * sp, size_t ssize, uint8_t rssi, uint8_t nodeid)
{
  Serial.write(0xAA);
  Serial.write(0x55);

  uint8_t crc = 0;
  for (uint8_t * ss = sp; ss < sp + ssize; ss++)
  {
    Serial.write(*ss);
    crc += *ss;
  }
  crc += nodeid;
  crc += rssi;
  crc  = (crc ^ 0xFF) + 1;

  Serial.write(nodeid);
  Serial.write(rssi);
  Serial.write(crc);
}


void setup() {

  Serial.begin(250000);
  pinMode(13, OUTPUT);
  writeDebug("Hello I am bob!");

}
uint16_t smt = 0;
void loop() {
  // put your main code here, to run repeatedly:
  sts.id = STATUS_TPACKET;
  sts.packets_sent = 123;
  sts.something = smt;

  unsigned long ss = millis();
  digitalWrite(13, HIGH);
  //writeStruct((uint8_t *)&sts, sizeof(sts), 40, 1);
  fakeData();
  writeStruct((uint8_t *)&data, sizeof(data), 66, 7);

  //fakeData();
  //writeStruct((uint8_t *)&data, sizeof(data), 66, 7);
  //delay(1000);

  writeDebug(100  );
  //delay(1000);
  delay(1000);
  smt++;
}

void fakeData()
{
  data.id = SENSORDATAPACKET;
  data.h1 = 1.1;
  data.t1 = 100.23;
  data.h2 = 2.2;
  data.t2 = 200.34;
  data.h3 = 3.3;
  data.t3 = 300.45;

  data.soil_t = 33;
  data.soil_h = 44;

  data.batt = 4.765;

  data.r = 1024;
  data.g = 2048;
  data.b = 32000;
  data.bob = 1;
}

