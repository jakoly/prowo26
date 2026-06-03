#include "libraries/SparkFun_TB6612/SparkFun_TB6612.h"

#define AIN1  4
#define AIN2  7
#define PWMA  5
#define STBY  9
#define ENC_A 2
#define ENC_B 3

Motor motor1 = Motor(AIN1, AIN2, PWMA, 1, STBY);

volatile long encoderTicks = 0;

void encoderISR() {
  static uint8_t prevState = 0;
  uint8_t state = (digitalRead(ENC_A) << 1) | digitalRead(ENC_B);
  static const int8_t table[] = {0,-1,1,0,1,0,0,-1,-1,0,0,1,0,1,-1,0};
  encoderTicks += table[(prevState << 2) | state];
  prevState = state;
}

long getEncoderTicks() {
  noInterrupts();
  long ticks = encoderTicks;
  interrupts();
  return ticks;
}

void resetEncoder() {
  noInterrupts();
  encoderTicks = 0;
  interrupts();
}

void setup() {
  Serial.begin(115200);
  pinMode(ENC_A, INPUT_PULLUP);
  pinMode(ENC_B, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENC_A), encoderISR, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC_B), encoderISR, CHANGE);
}

void loop() {
  motor1.drive(200);
  Serial.println(getEncoderTicks());
  delay(50);
}