#ifndef AD7606_H_
#define AD7606_H_

#include "SPI.h"

//ADC Channels (only four of the eight possible channels)
#define ADC_A 0
#define ADC_B 1
#define ADC_C 2
#define ADC_D 3

//channel setup register

//input range bits (RNG1, RNG0 bits)
#define PN_10 0 //positive/negative 10 volt
#define P_010 1 //positive, 0 to 10 volt
#define PN_5  2 //positive/negative 5 volt
#define P_05  3 //positive 0 to 5 volts

class AD7606 {
    public:
    AD7606();
    ~AD7606();

    //setup ADC SPI communication and pins used with the AD7606
    //cs: chip select pin, rdy: data ready pin, rst: ADC reset pin 
    void SetupAD7606(int cs, int rst, int busy, int convst);


    void ChannelSetup(int adc_channel, uint8_t flags);

    // Start a conversion
    void StartConversion();

    //request channel data from the ADC
    int GetConversionData();

    private:
    int _cs, _rdy, _rst, _busy, _convst;
    
    SPISettings adc_settings;
	
};

#endif