#include "INA219.h"

const int IN1 = 2;
const int IN2 = 3;
const int ENA = 4;
const int IN3 = 5;
const int IN4 = 6;
const int ENB = 7;
const int BUTTON = A0;
const int STICK  = A1;

INA219 INA(0x40);

// Gespeicherte Kalibrierzeit (ms) fuer Motor A und B
unsigned long calibratedTravelTimeA = 0;
unsigned long calibratedTravelTimeB = 0;

// ─── Hilfsfunktion: INA219-Messung ausgeben ──────────────────────────
void printMeasurements() {
  Serial.println("------------------------");
  Serial.print("Bus Voltage:   "); Serial.print(INA.getBusVoltage(), 3);       Serial.println(" V");
  Serial.print("Shunt Voltage: "); Serial.print(INA.getShuntVoltage_mV(), 3);  Serial.println(" mV");
  Serial.print("Current:       "); Serial.print(INA.getCurrent_mA() / 1000.0, 3); Serial.println(" A");
  Serial.print("Power:         "); Serial.print(INA.getPower_mW() / 1000.0, 3);  Serial.println(" W");
}

// ─── Motorsteuerung ──────────────────────────────────────────────────
void forward(int pin1, int pin2, int en, int speed) {
  digitalWrite(en, LOW); delay(10);
  digitalWrite(pin1, HIGH); digitalWrite(pin2, LOW);
  analogWrite(en, speed);
}

void backward(int pin1, int pin2, int en, int speed) {
  digitalWrite(en, LOW); delay(10);
  digitalWrite(pin1, LOW); digitalWrite(pin2, HIGH);
  analogWrite(en, speed);
}

void stopMotor(int pin1, int pin2, int en) {
  digitalWrite(en, LOW); delay(10);
  digitalWrite(pin1, LOW); digitalWrite(pin2, LOW);
}

// ─── Kalibrierung ────────────────────────────────────────────────────
unsigned long calibrate(int pin1, int pin2, int en) {
  Serial.println("\n=== STARTING CALIBRATION ===");
  Serial.println("Motor will run forward until it hits resistance (300 mA threshold)");
  Serial.println("Make sure there is an obstacle/wall ahead!");
  delay(2000);

  const float         RESISTANCE_THRESHOLD = 300.0;
  const unsigned long TIMEOUT             = 10000;
  const unsigned long RESISTANCE_DURATION  = 100;

  unsigned long startTime          = 0;
  unsigned long resistanceStartTime = 0;
  unsigned long lastPrint           = 0;
  float         maxCurrent          = 0;
  bool          resistanceDetected  = false;

  Serial.println("Starting motor...");
  forward(pin1, pin2, en, 255);
  delay(100);
  startTime = millis();

  while (!resistanceDetected) {
    float current = INA.getCurrent_mA();
    if (current > maxCurrent) maxCurrent = current;

    if (millis() - lastPrint > 100) {
      Serial.print("Current: "); Serial.print(current, 1);
      Serial.print(" mA  |  Time: "); Serial.print(millis() - startTime); Serial.println(" ms");
      lastPrint = millis();
    }

    if (current >= RESISTANCE_THRESHOLD) {
      if (resistanceStartTime == 0) {
        resistanceStartTime = millis();
        Serial.println(">>> Resistance detected! Confirming...");
      } else if (millis() - resistanceStartTime >= RESISTANCE_DURATION) {
        resistanceDetected = true;
      }
    } else {
      resistanceStartTime = 0;
    }

    if (millis() - startTime > TIMEOUT) {
      Serial.println("\n!!! CALIBRATION TIMEOUT !!!");
      Serial.print("Max current seen: "); Serial.print(maxCurrent, 1); Serial.println(" mA");
      stopMotor(pin1, pin2, en);
      return 0; // 0 signalisiert Fehler
    }
    delay(10);
  }

  stopMotor(pin1, pin2, en);

  unsigned long calibrationTime = millis() - startTime;
  Serial.println("\n=== CALIBRATION COMPLETE ===");
  Serial.print("Time to obstacle: "); Serial.print(calibrationTime); Serial.println(" ms");
  Serial.print("Peak current at impact: "); Serial.print(maxCurrent, 1); Serial.println(" mA");
  delay(2000);
  return calibrationTime; // BUG 1 BEHOBEN: Wert wird zurueckgegeben
}

// ─── Sequenz ─────────────────────────────────────────────────────────
void runSequence() {
  forward(IN1, IN2, ENA, 255); delay(300);
  printMeasurements(); // REDUNDANZ BEHOBEN

  stopMotor(IN1, IN2, ENA); delay(100);
  printMeasurements();

  backward(IN1, IN2, ENA, 150); delay(150);
  printMeasurements();

  stopMotor(IN1, IN2, ENA); delay(1000);
  printMeasurements();

  forward(IN3, IN4, ENB, 255); delay(5000);
  stopMotor(IN3, IN4, ENB);    delay(100);
  backward(IN3, IN4, ENB, 255); delay(5000);
  stopMotor(IN3, IN4, ENB);
}

// ─── travelDistance (jetzt funktionsfaehig) ──────────────────────────
void travelDistance(float percentage) {
  if (calibratedTravelTimeA == 0) {
    Serial.println("ERROR: Motor A not calibrated yet!"); return;
  }
  unsigned long travelTime = (unsigned long)(calibratedTravelTimeA * percentage / 100.0);
  Serial.print("Traveling "); Serial.print(percentage);
  Serial.print("% => "); Serial.print(travelTime); Serial.println(" ms");
  forward(IN1, IN2, ENA, 255); delay(travelTime); stopMotor(IN1, IN2, ENA);
}

// ─── Setup ───────────────────────────────────────────────────────────
void setup() {
  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT); pinMode(ENA, OUTPUT);
  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT); pinMode(ENB, OUTPUT);
  pinMode(BUTTON, INPUT_PULLUP);

  digitalWrite(ENA, LOW); digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(ENB, LOW); digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);

  Serial.begin(9600);
  while (!Serial);
  Wire.begin();

  if (!INA.begin()) {
    Serial.println("could not locate ina219 module");
    while (1) { delay(10); }
  }
  INA.setMaxCurrentShunt(5, 0.100);

  // BUG 2 BEHOBEN: Warte auf Button vor Kalibrierung
  Serial.println("Ready – press button to start calibration of Motor A...");
  while (digitalRead(BUTTON) != LOW) delay(20);
  delay(50); // Entprellen
  calibratedTravelTimeA = calibrate(IN1, IN2, ENA);

  Serial.println("Press button to start calibration of Motor B...");
  while (digitalRead(BUTTON) != LOW) delay(20);
  delay(50);
  calibratedTravelTimeB = calibrate(IN3, IN4, ENB);

  Serial.println("Setup complete.");
}

// ─── Loop ────────────────────────────────────────────────────────────
void loop() {
  int val = analogRead(STICK); // BUG 3 BEHOBEN: nur eine Deklaration

  if (digitalRead(BUTTON) == LOW) {
    delay(20);
    runSequence();
    while (digitalRead(BUTTON) == LOW) delay(20);
  }

  val = analogRead(STICK);
  if (val < 200) {
    forward(IN3, IN4, ENB, 255);
    while (analogRead(STICK) < 200) delay(20);
    stopMotor(IN3, IN4, ENB); // BUG 4 BEHOBEN: Motor stoppt beim Loslassen
  } else if (val > 800) {
    backward(IN3, IN4, ENB, 255);
    while (analogRead(STICK) > 800) delay(20);
    stopMotor(IN3, IN4, ENB); // BUG 4 BEHOBEN
  }
}