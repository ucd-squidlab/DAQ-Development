#include "Arduino.h"
#include "SPI.h"
#include "AD7606.h"

//ADC symbols
//All pages reference AD7606C-18 Data Sheet Rev A
//Communications Register, Table 11 Summery

//Read/Write bit, pg. 48
#define READ  1 << 6
#define WRITE 0 << 6

//First few ADC register addresses, table 31
#define ADDR_STATUS                   0x01
#define ADDR_CONFIG                   0x02
#define ADDR_RANGECH1CH2              0x03
#define ADDR_RANGECH3CH4              0x04
#define ADDR_RANGECH5CH6              0x05
#define ADDR_RANGECH7CH8              0x06
#define ADDR_BANDWIDTH                0x07
#define ADDR_OVERSAMPLING             0x08

//Address macro functions, returns address for desired register of selected channel (0-3), Table 11
#define ADDR_CHANNELDATA(adc_channel)   (0x8 + adc_channel)
#define ADDR_CHANNELZEROSCALECAL(adc_channel) (0x10 + adc_channel)
#define ADDR_CHANNELFULLSCALECAL(adc_channel) (0x18 + adc_channel)
#define ADDR_CHANNELSTATUS(adc_channel)(0x20 + adc_channel)
#define ADDR_CHANNELSETUP(adc_channel)(0x28 + adc_channel)
#define ADDR_CHANNELCONVERSIONTIME(adc_channel)(0x30 + adc_channel)
#define ADDR_MODE(adc_channel) (0x38 + adc_channel)

// Dout format: number of lines used for clocking out data via SPI
#define DOUTX1      0 << 3
#define DOUTX2      1 << 3
#define DOUTX4      2 << 3
#define DOUTX8      3 << 3


//resolution for 16 bit mode operation, the ADC supports 16 or 24 bit resolution.
#define ADCRES16 65535.0
//full scale range, can take 4 different values
#define FSR 20.0
#define ADC2DOUBLE(vin) (FSR * ((double)vin - (ADCRES16/2.0)) / ADCRES16) 

AD7606::AD7606() { }
AD7606::~AD7606() { }

//sets up the AD7606 SPI communication and pins 
void AD7606::SetupAD7606(int cs, int rst, int busy, int convst) {
    _cs = cs;
    _rst = rst;
    _busy = busy;
    _convst = convst;
    
    // Initial configuration
    status_header = ext_os_clock = dout_format = operation_mode = 0;
    
    // Keep track of what mode we're in right now. Default: ADC mode
    ADCMode = true;
    
	adc_settings = SPISettings(6000000, MSBFIRST, SPI_MODE3);
    

    
    //set bit order for ADC
    // SPI.setBitOrder(_cs, MSBFIRST);
    //set clock divider for DAC
    //SPI.setClockDivider(_cs, SPI_CLOCK_DIV64);
    //set data mode for dac
    // SPI.setDataMode(_cs, SPI_MODE2);

    //SPI.usingInterrupt(_rdy);

    //pinMode(_rdy, INPUT);
    pinMode(_busy, INPUT);
    pinMode(_convst, OUTPUT);
    pinMode(_rst, OUTPUT);
    pinMode(_cs, OUTPUT);

    
    // digitalWrite(_cs, HIGH);
    digitalWrite(_rst, HIGH);
    digitalWrite(_rst, LOW);
    
    delayMicroseconds(100);
    
    //begin SPI communication
    SPI.begin();
    digitalWrite(_cs, HIGH);
    
    // Set data output to all data lines. This will result
    // in 1 channel per data line instead of multiple channels
    // on the same data line.
    dout_format = DOUTX8;
    UpdateConfiguration();
    
    // Wait for board to finish initializing
    delayMicroseconds(100);
}

// Enables register mode by sending a read command
void AD7606::RegisterModeEnable() {
    ADCMode = false;
    // To enter register mode, we send a read command. The second byte is ignored.
    uint8_t data[2] = {READ | ADDR_CONFIG, 0}; 
    
    SPI.beginTransaction(adc_settings);
    digitalWrite(_cs, LOW);
    SPI.transfer(data, 2);
    digitalWrite(_cs, HIGH);
    
    SPI.endTransaction();
}

// Enables ADC mode by sending 2 bytes of zeros
void AD7606::ADCModeEnable() {
    ADCMode = true;
    uint8_t data[2] = {0, 0}; // Initialize a buffer of zeros
    
    // Send 2 bytes of zeros
    SPI.beginTransaction(adc_settings);
    digitalWrite(_cs, LOW);
    SPI.transfer(data, 2);
    digitalWrite(_cs, HIGH);
    SPI.endTransaction();
}

void AD7606::DiagnosticEnable() {
    if (ADCMode) {
        RegisterModeEnable();
    }
    // Register: 0x21
    // Bit 7 is for interface check
    uint8_t data[2] = {WRITE | 0x21, 1 << 7};
    SPI.beginTransaction(adc_settings);
    digitalWrite(_cs, LOW);
    SPI.transfer(data, 2);
    digitalWrite(_cs, HIGH);
    SPI.endTransaction();
    
    ADCModeEnable();
}

// Update the configuration register
void AD7606::UpdateConfiguration() {
    if (ADCMode) {
        RegisterModeEnable();
    }
    uint8_t config_data = status_header | ext_os_clock | dout_format | operation_mode;
    
    SPI.beginTransaction(adc_settings);
    digitalWrite(_cs, LOW);
    SPI.transfer(ADDR_CONFIG);
    SPI.transfer(config_data);
    digitalWrite(_cs, HIGH);
    SPI.endTransaction();
}

//tells the ADC to start a conversion
void AD7606::StartConversion() {
    // A conversion is triggered by a low followed by a high on the _convst pin
    digitalWrite(_convst, LOW);
    digitalWrite(_convst, HIGH);

    //data is ready when _busy goes low
}


uint32_t AD7606::GetConversionData() {
    if (!ADCMode) {
        ADCModeEnable();
    }
    uint8_t upper = 0xAF, middle = 0x0A, lower = 0xF0; // Values for testing
    
    SPI.beginTransaction(adc_settings);
    digitalWrite(_cs, LOW);

    //read result
    upper = SPI.transfer(0);
    middle = SPI.transfer(0);
    lower = SPI.transfer(0);
    
    
    digitalWrite(_cs, HIGH);
    SPI.endTransaction();

    // Convert
    uint32_t result = ((upper&0xff)<<16 | (middle&0xff) << 8 | (lower&0xff));
    
    return result;
}