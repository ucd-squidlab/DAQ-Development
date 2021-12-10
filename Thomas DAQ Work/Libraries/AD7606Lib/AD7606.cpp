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

//Operational Mode Register, Table 12
//mode bits (MD2, MD1, MD0 bits)
#define IDLE_MODE                   0 << 5
#define CONT_CONV_MODE              1 << 5
#define SINGLE_CONV_MODE            2 << 5
#define PWR_DOWN_MODE               3 << 5
#define ZERO_SCALE_SELF_CAL_MODE    4 << 5
#define CH_ZERO_SCALE_SYS_CAL_MODE  6 << 5
#define CH_FULL_SCALE_SYS_CAL_MODE  7 << 5
#define CH_EN_CONT_CONV             1 << 3

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
    
	adc_settings = SPISettings(60000000, MSBFIRST, SPI_MODE2);
    

    //being SPI communication on the ADC chip select
    SPI.begin();
    
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


    digitalWrite(_rst, HIGH);
    digitalWrite(_rst, LOW);
    delayMicroseconds(100);
    
    // Set data output to all data lines. This will result
    // in 1 channel per data line instead of multiple channels
    // on the same data line.
    dout_format = DOUTX8;
    UpdateConfiguration();
    
    // Wait for board to finish initializing
    delayMicroseconds(100);
}


// Update the configuration register
void AD7606::UpdateConfiguration() {
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


int AD7606::GetConversionData() {
    uint8_t data_array, upper, middle, lower;
    
    SPI.beginTransaction(adc_settings);
    digitalWrite(_cs, LOW);

    //read bytes of channel data register (16 bit mode)
    upper = SPI.transfer(0);
    middle = SPI.transfer(0);
    lower = SPI.transfer(0);
    
    digitalWrite(_cs, HIGH);
    SPI.endTransaction();

    // Convert
    int result = ((upper&0xff)<<10 | (middle&0xff) << 2 | (lower&0xff) >> 6);
    
    return result;
}