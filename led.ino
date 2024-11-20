#include <Adafruit_NeoPixel.h>

#define PIN 2
#define NUMPIXELS 64

Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

const char* chessBoardSquares[64] = {
  "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1",
  "a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2",
  "a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3",
  "a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4",
  "a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5",
  "a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6",
  "a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7",
  "a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8"
};

void setup() {
  Serial.begin(9600);
  pixels.begin();
  pixels.clear();
  
}

int getChessSquareLEDIndex(String squareName) {
  for (int i = 0; i < 64; i++) {
    if (squareName == chessBoardSquares[i]) {
      return i;
    }
  }
  return -1;
}

uint32_t getColorCode(String color) {
  if (color == "b") return pixels.Color(0, 0, 255);    // Blue
  if (color == "r") return pixels.Color(255, 0, 0);    // Red
  if (color == "y") return pixels.Color(255, 255, 0);  // Yellow
  return pixels.Color(0, 0, 0);  // Default to off
}

void processInput(String input) {
  int start = 0;
  int comma = input.indexOf(',');
  
  pixels.clear();  // Clear previous LED states
  
  while (comma != -1) {
    String entry = input.substring(start, comma);
    entry.trim();
    
    int slashIndex = entry.indexOf('/');
    if (slashIndex != -1) {
      String square = entry.substring(0, slashIndex);
      String colorCode = entry.substring(slashIndex + 1);
      
      int ledIndex = getChessSquareLEDIndex(square);
      if (ledIndex != -1) {
        pixels.setPixelColor(ledIndex, getColorCode(colorCode));
        Serial.print("Setting ");
        Serial.print(square);
        Serial.print(" to ");
        Serial.println(colorCode == "b" ? "blue" : (colorCode == "r" ? "red" : "yellow"));
      }
    }
    
    start = comma + 1;
    comma = input.indexOf(',', start);
  }
  
  // Process last entry
  String lastEntry = input.substring(start);
  lastEntry.trim();
  
  int slashIndex = lastEntry.indexOf('/');
  if (slashIndex != -1) {
    String square = lastEntry.substring(0, slashIndex);
    String colorCode = lastEntry.substring(slashIndex + 1);
    
    int ledIndex = getChessSquareLEDIndex(square);
    if (ledIndex != -1) {
      pixels.setPixelColor(ledIndex, getColorCode(colorCode));
      Serial.print("Setting ");
      Serial.print(square);
      Serial.print(" to ");
      Serial.println(colorCode == "b" ? "blue" : (colorCode == "r" ? "red" : "yellow"));
    }
  }
  
  pixels.show();
}

void loop() {
  if (Serial.available() > 0) {
    String receivedInput = Serial.readStringUntil('\n');
    receivedInput.trim();
    
    processInput(receivedInput);
  }
}
