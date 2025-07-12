#include <Arduino.h>

#define ROW_PINS {34, 35, 32, 33, 25, 26, 27, 14}
#define COL_PINS {12, 13, 23, 22, 21, 19, 18, 5}

const int rowPins[] = ROW_PINS;
const int colPins[] = COL_PINS;

void displayFrame(uint8_t *frame)
{
  // Faster scanning with optimized timing
  for (int row = 0; row < 8; row++)
  {
    // Quickly disable all rows and columns first
    for (int i = 0; i < 8; i++)
    {
      digitalWrite(rowPins[i], HIGH);
      digitalWrite(colPins[i], LOW);
    }

    // Set column states for current row
    for (int col = 0; col < 8; col++)
    {
      bool pixelOn = (frame[row] >> (7 - col)) & 1;
      digitalWrite(colPins[col], pixelOn ? HIGH : LOW);
    }

    // Enable current row
    digitalWrite(rowPins[row], LOW);

    // Reduced delay for faster refresh rate
    delayMicroseconds(50);
  }
}

void setup()
{
  Serial.begin(115200);
  delay(1000);
  Serial.println("Starting LED Matrix Test");

  // Initialize and test all pins
  for (int i = 0; i < 8; i++)
  {
    pinMode(rowPins[i], OUTPUT);
    pinMode(colPins[i], OUTPUT);
    digitalWrite(rowPins[i], HIGH);
    digitalWrite(colPins[i], LOW);

    Serial.print("Initialized Row Pin: ");
    Serial.print(rowPins[i]);
    Serial.print(", Col Pin: ");
    Serial.println(colPins[i]);
  }

  // Test each row/column combination
  Serial.println("Testing individual pixels...");
  for (int row = 0; row < 8; row++)
  {
    for (int col = 0; col < 8; col++)
    {
      // Clear all
      for (int i = 0; i < 8; i++)
      {
        digitalWrite(rowPins[i], HIGH);
        digitalWrite(colPins[i], LOW);
      }

      // Light single pixel
      digitalWrite(colPins[col], HIGH);
      digitalWrite(rowPins[row], LOW);

      Serial.print("Testing Row ");
      Serial.print(row);
      Serial.print(" (Pin ");
      Serial.print(rowPins[row]);
      Serial.print("), Col ");
      Serial.print(col);
      Serial.print(" (Pin ");
      Serial.print(colPins[col]);
      Serial.println(")");

      delay(200);
    }
  }

  // Clear all after test
  for (int i = 0; i < 8; i++)
  {
    digitalWrite(rowPins[i], HIGH);
    digitalWrite(colPins[i], LOW);
  }

  Serial.println("Pin test complete. Starting animation...");
}

void loop()
{
  // Quick test: all rows HIGH, all columns LOW
  for (int i = 0; i < 8; i++)
  {
    digitalWrite(rowPins[i], HIGH);
    digitalWrite(colPins[i], LOW);
  }

  delay(1000);
}