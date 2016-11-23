#include "test.h"
SensorData data;
struct Status_t sts;

void writeStruct(uint8_t * sp, size_t ssize)
{
  Serial.write(0xAA);
  Serial.write(0x55);

  uint8_t crc = 0;
  for (uint8_t * ss = sp; ss < sp + ssize; ss++)
  {
    Serial.write(*ss);
    crc += *ss;
  }

  crc  = (crc ^ 0xFF) + 1;
  Serial.write(crc);
}


void setup() {

  Serial.begin(115200);

  sts.id=STATUS_TPACKET;
  sts.packets_sent = 123;
  sts.something = 12;
  writeStruct((uint8_t *)&sts, sizeof(sts));
}

void loop() {
  // put your main code here, to run repeatedly:

}
