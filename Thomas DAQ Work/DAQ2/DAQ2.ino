
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

#define LED 13

//buffer size for ADC converstions
#define BUFFERSIZE 2
//ADC conversion data buffer
volatile uint8_t adc_data[4][BUFFERSIZE];
int adc_response;

void setup() {    
    //begin serial communication with a BAUD rate of 115200
    Serial.begin(115200);

    //setup the DAC (see the AD5764 library for details)
    dac.SetupAD5764(DAC_CS, DAC_LDAC, DAC_CLR);
    //setup the ADC (see the AD7606 library for details)
    adc.SetupAD7606(ADC_CS, ADC_RDY, ADC_RST, ADC_BSY, ADC_CONVST);

    //setup LED pin for output
    //pinMode(LED, OUTPUT);
}

void loop() {
    //wait for a valid 16 byte data stream to become available

    //if Serial.available() % 16 != 0 after a communication is completed, then the Arduino will not process
    //the bitstream properly, the fastest way to fix this is a restart, the input stream can also be flushed with data
    //until Serial.available() % 16 == 0.
    
    if (Serial.available() >= 16) {
        //read 16 bytes of serial data into a data buffer
        uint8_t data[16];
        Serial.readBytes(data, 16);

        //get function code (upper 4 bits from first data byte)
        uint8_t fnc = data[0] >> 4;
        byte adc_data[2];
        byte somedata[] = {1, 15, 9};

        //branch based on function code 
        switch (fnc) {
            case 0:
                //digitalWrite(LED, HIGH);
                //change the voltage on the passed DAC channel to the passed voltage 
                dac.SetDataRegister((data[1] << 8) | data[2], (data[0] >> 2) & 0x3);
            break;

            case 1:
                //begin ADC conversion on the passed channels 
                adc.StartConversion();
                delayMicroseconds(100);
                adc_response = adc.GetConversionData();
            break;

            case 2:
                //digitalWrite(LED, LOW);
                //write back the requested ADC conversion data 
//                Serial.write((uint8_t*)(adc_data[data[0] & 0x3]), 2);

                adc_data[0] = (adc_response >> 16)&0xFF;
                adc_data[1] = (adc_response >> 8)&0xFF;
                adc_data[2] = (adc_response)&0xFF;
//                Serial.write(adc_data, 3);
                Serial.write(adc_data, 3);
            default:
            break;
        }
    }
}
