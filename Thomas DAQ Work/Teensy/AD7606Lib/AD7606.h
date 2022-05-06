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
    void SetupAD7606(int cs, int rst, int busy, int convst, int baudrate = 10000000);


    void ChannelSetup(int adc_channel, uint8_t flags);
    
    void UpdateConfiguration();

    // Start a conversion
    void StartConversion();
    
    
    void InterfaceCheckMode(bool enable);
    void FullReset();
    void GainCalibration(uint8_t val);
    void HighSampleRate(bool enable);

    //request channel data from the ADC
    uint32_t GetConversionData(uint8_t channel);
    void GetConversionDataFast(uint8_t (& result)[3]);
    

    private:
    int _cs, _rst, _busy, _convst;
    uint8_t status_header, ext_os_clock, dout_format, operation_mode;
    bool ADCMode;
    bool diagnosticMode;
    bool uptodate;
    
    void RegisterModeEnable();
    void ADCModeEnable();
    void RegisterWrite(uint8_t reg, uint8_t data);
    
    SPISettings adc_settings;
    
    // Not used yet. One idea was to store
    // ADC readings immediately after a conversion using the BUSY line
    // as a trigger, and then read from this array instead of
    // sending new SPI commands to the ADC.
    // Another idea was to use this in the GetConversionData function.
    uint32_t adc_reading[8] {0};
	
};

#endif