#include <Arduino.h>
#ifndef __TEST_H
#define __TEST_H

#define SENSORDATAPACKET 0x01
#define STATUS_TPACKET 0x02

typedef struct {
  uint8_t id ;
  float h1 ;
  float t1;
  float h2;
  float t2;
  float h3;
  float t3;

  float soil_t;
  float soil_h;

  float batt;

  uint16_t r ;
  uint16_t g;
  uint16_t b;
  uint32_t bob;
} 
SensorData;

struct Status_t
{
  uint8_t id;
  uint16_t packets_sent;
  uint16_t something;
  
};

#endif __TEST_H
