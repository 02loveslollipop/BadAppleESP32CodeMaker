#include <ESP_8_BIT_composite.h>
#include "byteStream.h"

ESP_8_BIT_composite videoOut(true /* = NTSC */);

uint32_t streamPointer;
uint8_t** frameBufferLines;

int printFrame(uint32_t pointer){
  unsigned char line = 0;
  bool deprecateNextByte = false;
  bool firstFF = false;
  int i = 0;
  
  for (i = pointer; i <= totalFrames; i++) {
    if (byteStream[i] == 0xFF) {
      if(firstFF){
        return i;
      }else{
      line = byteStream[i + 1];
      deprecateNextByte = true;
      firstFF = true;
      }
    } else if (byteStream[i] == 0xFE) {
      line = byteStream[i + 1];
      deprecateNextByte = true;
    } else if (deprecateNextByte) {
      deprecateNextByte = false;
    } else {
      frameBufferLines[line][byteStream[i]] = (frameBufferLines[line][byteStream[i]] == 0xFF) ? 0x00 : 0xFF;
    }
  }
  return i;
}

void setup() {
  videoOut.begin();
  frameBufferLines = videoOut.getFrameBufferLines();
  streamPointer = 0;
  for (int y = 0; y < 240; y++)
  {
    for (int x = 0; x < 256; x++)
    {
      frameBufferLines[y][x] = 0x00;
    }
  }

  videoOut.waitForFrame();
}

void loop() {
  streamPointer = printFrame(streamPointer);
  delay(delayMS);
  delayMicroseconds(delayUS);
}

