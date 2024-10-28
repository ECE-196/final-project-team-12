struct LidarPointStructDef { 
  uint16_t distance;
  uint8_t intensity;
};

struct LiDARFrame {
  uint8_t header;   // start byte (0x54)
  uint8_t ver_len;
  uint16_t speed;
  uint16_t startangle;
  LidarPointStructDef data[12];
  uint16_t end_angle;
  uint16_t timestamp;
  uint8_t crc8;
};



int dataList[47];

void setup() {
    Serial.begin(230400);   // For Serial Monitor
    Serial1.begin(230400);  // For Serial1 communication
}

void printDatalist(){
  for (int i = 0; i < 47; i++) {
    if(dataList[i] < 16){
      Serial.print("0");
    }
    Serial.print(dataList[i], HEX);
    Serial.print(" ");
  }
  Serial.println();
}


/*
void loop() {
    // Check if data is available on Serial1
    if (Serial1.available()) {
      int incomingByte = Serial1.read();
      if (incomingByte == 84) {     //0x54 is the start byte
        dataList[0] = incomingByte;
        for (int i = 1; i < 47; i++) {
          if (Serial1.available()) {
            dataList[i] = Serial1.read();
          }
        }

      printDatalist();
    }
  }
}
*/

void loop(){
  if (Serial1.available()) {
    Serial.println(Serial1.read(), HEX);
  }
}


/*
54 49 21 2C 10 00 1D 00 75 00 1D 00 1D 00 1D 00 1D 00 1D 00 75 00 75 00 75 00 74 00 60 08 C5 79 54 2C 2F 08 43 00 D4 00 75 00 1D 00 1D 00 1D 
54 E9 21 43 21 00 1D 00 75 00 1D 00 1D 00 1D 00 1D 00 1D 00 75 00 75 00 75 00 74 00 60 59 A8 31 FF 54 E9 21 CC 43 00 1D 00 75 00 1D 00 1D 00 
54 E9 21 56 04 00 1D 00 75 00 1D 00 1D 00 1D 00 1D 00 1D 00 75 00 75 00 75 00 74 00 60 4D B4 31 FC 54 49 21 E5 22 00 1D 00 75 00 1D 00 1D 00 
54 49 21 71 45 00 1D 00 75 00 1D 00 1D 00 1D 00 1D 00 1D 00 D5 00 75 00 75 00 74 00 60 DC 14 31 EA 54 49 21 FD 11 00 1D 00 75 00 1D 00 1D 00 
54 E9 21 11 47 00 1D 00 75 00 1D 00 1D 00 1D 00 1D 00 1D 00 75 00 75 00 75 00 74 00 60 D6 A4 31 1D 00 1D 00 1D 00 1D 00 00 75 00 1D 00 1D 00 
54 49 21 25 24 00 1D 00 75 00 1D 00 1D 00 1D 00 1D 00 D4 00 75 00 75 00 75 00 74 00 60 17 02 31 F5 54 49 21 AB 12 00 1D 00 75 00 1D 00 1D 00 
54 09 08 D3 02 00 1D 00 75 00 1D 00 1D 00 1D 00 1D 00 D4 00 75 00 75 05 70 2A D0 2A D4 2C 32 31 FA 54 09 08 5C 49 05 D4 2A D4 15 D4 15 D4 56 
54 09 08 2A C9 05 D4 00 DD 05 D4 15 D4 55 D4 55 D4 15 D4 15 D5 2A D5 2A D5 2A D5 2A C5 9A 89 8B 8D 54 69 21 DB 49 05 8B 00 1D 00 1D 00 1D 00 
54 69 21 60 4C 00 31 00 1D 00 1D 00 1D 00 1D 00 1D 00 1D 00 75 00 75 00 75 00 75 00 71 B6 92 31 54 69 21 EA 26 00 31 00 1D 00 1D 00 1D 00 1D 
54 49 21 73 13 00 31 00 1D 00 1D 00 1D 00 1D 00 1D 00 1D 00 75 00 75 00 75 00 75 00 71 0E C2 31 F1 54 49 21 FF 02 00 31 00 1D 00 1D 00 1D 00 
54 49 21 84 27 00 31 00 1D 00 1D 00 1D 00 1D 00 1D 00 1D 00 75 00 75 00 75 00 75 00 71 D7 F2 31 F1 54 49 21 0F 02 00 31 00 1D 00 1D 00 1D 00 
54 49 21 1A 43 00 31 00 1D 00 1D 00 1D 00 1D 00 1D 00 1D 00 75 00 75 00 75 00 75 00 71 AB 1D 00 1D 00 1D 00 75 00 00 31 75 1D 00 1D 00 1D 00 
54 49 21 31 2A 05 4F 2A 5B 2A 6D 2A AB 2A D5 2A D5 15 D5 15 D4 55 D4 55 D4 15 D4 15 D4 29 35 31 FE 54 69 21 B3 A9 15 D4 15 D4 05 D4 05 D4 05 
54 69 21 36 53 15 D5 2A D5 2A D5 2A A5 00 1D 00 1D 00 75 00 1D 00 1D 00 1D 00 1D 00 75 D8 6A 17 52 54 69 21 BC 0A 00 D5 00 75 00 75 75 24 59 
54 E9 21 46 2A 00 75 00 75 00 75 00 69 00 1D 00 1D 00 75 00 1D 00 1D 00 1D 00 1D 00 75 46 65 31 E3 54 E9 21 CF 15 00 75 00 75 00 75 00 69 00 
54 89 21 5C 15 00 75 00 75 00 75 00 69 00 1D 00 1D 00 75 00 1D 00 1D 00 1D 00 1D 00 75 2D F5 31 D5 54 89 21 E3 56 00 75 00 75 00 75 00 69 00 
54 89 21 69 05 00 75 00 75 00 75 00 69 00 1D 00 1D 00 75 00 1D 00 1D 00 1D 00 1D 00 75 37 55 31 FF 54 C9 21 F1 05 00 75 00 75 00 75 00 69 00 
54 C9 21 00 16 00 75 00 75 00 D5 00 69 00 1D 00 1D 00 00 75 00 69 00 1D 00 1D 00 00 75 37 55 31 FF 54 C9 21 F1 75 00 75 00 75 00 75 00 69 00 
54 2C 2F 08 43
54 E9 21 CC 43
54 49 21 E5 22
54 49 21 FD 11



33 bytes total (???)




*/

/*
54 9 21 75 44 0 75 0 72 0 1D 0 1D 0 1D 0 0 0 75 0 0 DC A3 numba: 23
54 9 21 FC 22 0 75 0 72 0 0 1D 1D 0 1D 75 75 0 0 75 29 6D numba: 22
54 9 21 7F 11 0 75 0 72 0 0 1D 0 0 1D 75 75 0 0 88 numba: 20
54 69 21 8 46 0 75 0 72 0 1D 0 1D 0 0 1D 1D 75 75 0 75 75 numba: 22
54 69 21 8E 23 0 75 0 72 0 1D 0 1D 0 0 1D 75 75 0 0 75 45 numba: 22
54 69 21 15 4 0 75 0 72 0 1D 0 1D 1D 1D 0 0 0 0 0 numba: 20
54 29 21 9F 2 0 75 0 72 0 1D 0 1D 0 D4 0 1D 75 0 75 75 4F numba: 22
54 29 21 25 24 5 6F 2A 9D 2A D5 15 D5 CA BA 1D 75 0 75 0 numba: 20
*/
/*
// This code ignores the "12 bytes of data" and just returns a new line
int count = 0;
void loop() {
  if (Serial1.available()) {
    int incomingByte = Serial1.read();
    if (incomingByte == 84) {     //0x54 is the start byte
      
      Serial.println("numba: " + String(++count));
      count = 0;
      Serial.print(incomingByte, HEX);
      Serial.print(" ");

    } else {
      if(incomingByte < 16){
        Serial.print(" ");
      }
      Serial.print(incomingByte, HEX);
      count++;
      Serial.print(" ");
    }
  }
}
*/


