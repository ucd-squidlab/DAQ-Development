/** Version 22.02.4
 * (year.month.commit#)
 * 
 * Serial commands
 * ---------------
 * 
 * Each serial command consists of 16 bytes of data. The first 4
 * bits contain the command ID. The rest is data.
 * 
 * 
 * 0. Set DAC
 *    Code: 0
 *    Data[0], bits 3-0: Channel (0-4)
 *    Data[1]-Data[2]: Voltage, (-10) to (+10)
 *    Data[3]: Send completion alert (0 = no alert)
 *    
 *    Set an output voltage on the given DAC channel.
 *    Channels range from 0-3. Use a value of 4 to set all channels.
 *    If byte 3 is nonzero, the Teensy will send a response code after the
 *    voltage has been updated on the DAC. This is useful if the voltage
 *    slew rate has been limited. A response code of 0 means success.
 * 
 * 
 * 1. Begin ADC Conversion
 *    Code: 1
 *    
 *    Trigger an ADC conversion.
 *    
 *    
 * 2. Get ADC Reading
 *    Code: 2
 *    
 *    Trigger an ADC conversion, read the result, and
 *    return result in 3 bytes over serial. The first 18 bits
 *    of the result contain the ADC reading.
 *    
 *    
 * 3. Interface Check Diagnostic Mode
 *    Code: 3
 *    Data[0], bits 4-0: 1 = enable, 0 = disable
 *    
 *    Enables or disables the ADC diagnostic interface check. When
 *    enabled, ADC conversions return a fixed value. This can be used to
 *    determine whether the SPI interface is functioning properly.
 *    
 *    
 * 4. Reset ADC
 *    Code: 4
 *    
 *    Reset the ADC. LED will toggle for half a second.
 * 
 */
//DAC library header
#include <AD5764.h>
//ADC library header
#include <AD7606.h>
//Arduino SPI library header
#include "SPI.h"
#include <algorithm>

using namespace std;

//instance of the AD5764 class ( DAC )
AD5764 dac;
//instance of the AD7734 class ( ADC )
AD7606 adc;

//pins for adc and dac 
//DAC chip select pin 
//#define DAC_CS 4
#define DAC_CS 36
//DAC LDAC pin
#define DAC_LDAC 6
//DAC clear pin
#define DAC_CLR 5
#define DAC_RES 16

//ADC chips select pin
#define ADC_CS 10
//ADC data ready pin
#define ADC_RDY 0
//ADC reset pin 
//#define ADC_RST 44
#define ADC_RST 31
#define ADC_RES 18

#define ADC_BSY 32
#define ADC_CONVST 30

#define LED 33

//buffer size for ADC converstions
#define BUFFERSIZE 2
//ADC conversion data buffer
volatile uint8_t adc_data[4][BUFFERSIZE];
int adc_response;

long fft[50000];
byte buf[200000];
bool LEDState = false;

// How long to change an output voltage, in microseconds per step.
// NOTE: This feature assumes that a value of 0x0000 corresponds
// to the minimum possible voltage and 0xFFFF corresponds to the
// maximum voltage. If the DAC library is changed, then
// the feature may need to be rewritten.
// *** NOT IMPLEMENTED ***
uint16_t DACDeltaT[4] = {20, 0, 0, 0};
// Step size when changing the DAC output voltage, in LSB
uint8_t DACStepSize = 1;


// Current state of DAC
// *** NOT IMPLEMENTED ***
uint16_t DACVout[4] = {1<<15};

void setup() {
    //begin serial communication with a BAUD rate of 115200
    Serial.begin(250000);

    //setup the DAC (see the AD5764 library for details)
    dac.SetupAD5764(DAC_CS, DAC_LDAC, DAC_CLR);
    //setup the ADC (see the AD7606 library for details)
    adc.SetupAD7606(ADC_CS, ADC_RST, ADC_BSY, ADC_CONVST, 10000000);

    //setup LED pin for output
    pinMode(LED, OUTPUT);

    digitalWrite(LED, HIGH);
    LEDState = true;

    adc.GainCalibration(0x00);
    SetDAC(1<<15, 4);
}

void fftToBuf(){
  for (int i = 0;i < 10000;i++){
    buf[i*4]=((fft[i]>>24)&0xFF);
    buf[i*4+1]=((fft[i]>>16)&0xFF);
    buf[i*4+2]=((fft[i]>>8)&0xFF);
    buf[i*4+3]=(fft[i]&0xFF);
  }
}

void LEDToggle() {
  LEDState = !LEDState;
  if (LEDState) {
    digitalWrite(LED, HIGH);
  } else {
    digitalWrite(LED, LOW);
  }
}


// Start an ADC conversion, get the data, and send it to host over USB serial
void GetADCReading() {
    adc.StartConversion();
    delayMicroseconds(1000);
    adc_response = adc.GetConversionData();
    
    
    byte adc_data[3];
    adc_data[0] = (adc_response >> 16)&0xFF;
    adc_data[1] = (adc_response >> 8)&0xFF;
    adc_data[2] = (adc_response)&0xFF;

    //byte otherdata[3] = {0xFB, 0xAD, 0x0A}; //debug
    Serial.write(adc_data, 3);
}

// Set the DAC output on channel `channel` to voltage `vout`
// where `vout` is encoded assuming that 0x0000 = -10V and
// 0xFFFF = 10V
int SetDAC(uint16_t vout, uint8_t channel) {
  // Get the deltaT for each step
  uint16_t deltaT;

  // Get time delay for each step
  if (channel == 4) {
    deltaT = *std::max_element(DACDeltaT, DACDeltaT+4);
    if (deltaT > 0) {
      // Abort if there are slew rate restrictions on any channels.
      return -1;
    }
  } else {
    deltaT = DACDeltaT[channel];
  }

  // Set voltage
  if (deltaT == 0) {
    if (channel == 4) {
      std::fill(DACVout, DACVout+4, vout);
    } else {
      DACVout[channel] = vout;
    }
    dac.SetDataRegister(vout, channel);
    
  } else { // We already made sure only 1 channel is being changed when deltaT>0
    
    // Direction (increasing or decreasing voltage)
    int dir = 2*(vout > DACVout[channel]) - 1; // 1 if increasing, -1 if decreasing
    bool complete = false;
    while(!complete) {
      DACVout[channel] += dir*DACStepSize;
      if (dir*DACVout[channel] >= dir*vout) {
        DACVout[channel] = vout;
        complete = true;
      }
      dac.SetDataRegister(DACVout[channel], channel);
      delayMicroseconds(deltaT);
    }
  }
  return 0;
}

void loop() {
    //wait for a valid 16 byte data stream to become available

    //if Serial.available() % 16 != 0 after a communication is completed, then the Arduino will not process
    //the bitstream properly, the fastest way to fix this is a restart, the input stream can also be flushed with data
    //until Serial.available() % 16 == 0.

    
    if (Serial.available() >= 16) {
        //read 16 bytes of serial data into a data buffer
        unsigned char data[16];
        Serial.readBytes(data, 16);

        //get function code (upper 4 bits from first data byte)
        uint8_t fnc = data[0] >> 4;

        bool enable;
        unsigned char response_code;

        //branch based on function code 
        switch (fnc) {                
            case 0:
                response_code = 0;
                //change the voltage on the passed DAC channel to the passed voltage 
                SetDAC((data[1] << 8) | data[2], data[0] & 0x7);
                if (data[3] > 0) {
                  Serial.write(response_code);
                }
                break;

            case 1:
                //begin ADC conversion
                adc.StartConversion();
                delayMicroseconds(100);
                adc_response = adc.GetConversionData();
                break;

            case 2:
                // Start ADC conversion, get result, send result over serial
                GetADCReading();
                break;

            case 3:
                // Interface check mode
                enable = data[0] & 0xF; // Whether to enable or disable
                adc.InterfaceCheckMode(enable);
                break;

            case 4:
                // Reset ADC
                LEDToggle();
                adc.FullReset();
                delay(500);
                LEDToggle();
                break;

            case 5:
                break;
            
            default:
                LEDToggle();
        }
    }
}
