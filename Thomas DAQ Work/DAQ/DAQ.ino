
//DAC library header
#include <AD5764.h>
//ADC library header
#include <AD7606.h>
//Arduino SPI library header
#include "SPI.h"

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

//ADC chips select pin
#define ADC_CS 10
//ADC data ready pin
#define ADC_RDY 0
//ADC reset pin 
//#define ADC_RST 44
#define ADC_RST 31

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

void setup() {    
    //begin serial communication with a BAUD rate of 115200
    Serial.begin(250000);

    //setup the DAC (see the AD5764 library for details)
    dac.SetupAD5764(DAC_CS, DAC_LDAC, DAC_CLR);
    //setup the ADC (see the AD7606 library for details)
    adc.SetupAD7606(ADC_CS, ADC_RST, ADC_BSY, ADC_CONVST);

    //setup LED pin for output
    pinMode(LED, OUTPUT);

    digitalWrite(LED, HIGH);
    LEDState = true;

    // Take 5 seconds of ADC measurements at 10 kHz and
    // output over serial. This tests whether the libraries
    // are working properly.
    long output;
    unsigned long cputime, cputime2,wait;
    wait = 0;
    cputime2 = micros();
    for (int i = 0;i < 50000;i++){
        while(wait>micros()){}
        cputime = micros();
        wait = cputime+99;
        adc.StartConversion();
        delayMicroseconds(5);
        fft[i] = adc.GetConversionData();
    }
    cputime = micros();
    fftToBuf();
    Serial.write(buf,40000);
    Serial.println(micros()-cputime);

    LEDToggle();
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
    LEDToggle();
    delayMicroseconds(100);
    adc_response = adc.GetConversionData();
    
    
    byte adc_data[3];
    adc_data[0] = (adc_response >> 16)&0xFF;
    adc_data[1] = (adc_response >> 8)&0xFF;
    adc_data[2] = (adc_response)&0xFF;
    Serial.write(adc_data, 3);
}




void loop() {
    //wait for a valid 16 byte data stream to become available

    //if Serial.available() % 16 != 0 after a communication is completed, then the Arduino will not process
    //the bitstream properly, the fastest way to fix this is a restart, the input stream can also be flushed with data
    //until Serial.available() % 16 == 0.

    
    if (Serial.available() >= 16) {
        //read 16 bytes of serial data into a data buffer
        byte data[16];
        Serial.readBytes(data, 16);

        //get function code (upper 4 bits from first data byte)
        char fnc = data[0] >> 4;

        //branch based on function code 
        switch (fnc) {
            case 0:
                LEDToggle();
                //change the voltage on the passed DAC channel to the passed voltage 
                dac.SetDataRegister((data[1] << 8) | data[2], (data[0] >> 2) & 0x3);
            break;

            case 1:
                //begin ADC conversion
                adc.StartConversion();
                delayMicroseconds(100);
                adc_response = adc.GetConversionData();
            break;

            case 2:
                GetADCReading();
            default:
            break;
        }
    }
}
