#include "Arduino.h"
#include "SPI.h"
#include "AD7606.h"

//ADC symbols
//All tables & pages reference AD7734 Data Sheet Rev B (4 Channels, AD7732 is 2 Channels)
//Communications Register, Table 11 Summery

//Read/Write bit (R, W), Table 11
#define READ  1 << 6
#define WRITE 0 << 6

//ADC register addresses, Table 11
#define ADDR_COM                      0x0
#define ADDR_IO                       0x1
#define ADDR_REVISION                 0x2
#define ADDR_TEST                     0x3
#define ADDR_ADCSTATUS                0x4
#define ADDR_CHECKSUM                 0x5
#define ADDR_ADCZEROSCALECAL          0x6
#define ADDR_ADCFULLSCALE             0x7

//Address macro functions, returns address for desired register of selected channel (0-3), Table 11
#define ADDR_CHANNELDATA(adc_channel)   (0x8 + adc_channel)
#define ADDR_CHANNELZEROSCALECAL(adc_channel) (0x10 + adc_channel)
#define ADDR_CHANNELFULLSCALECAL(adc_channel) (0x18 + adc_channel)
#define ADDR_CHANNELSTATUS(adc_channel)(0x20 + adc_channel)
#define ADDR_CHANNELSETUP(adc_channel)(0x28 + adc_channel)
#define ADDR_CHANNELCONVERSIONTIME(adc_channel)(0x30 + adc_channel)
#define ADDR_MODE(adc_channel) (0x38 + adc_channel)

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
    SPI.beginTransaction(adc_settings);
    digitalWrite(_cs, LOW);
    SPI.transfer(0x02);
    SPI.transfer(0x18);
    digitalWrite(_cs, HIGH);
    SPI.endTransaction();
    
    // Wait for board to finish initializing
    delayMicroseconds(100);
}


// Not sure we need this method so I commented out everything inside.
void AD7606::ChannelSetup(int adc_channel, uint8_t flags) {
    // uint8_t data_array[2];

    // data_array[0] = WRITE | ADDR_CHANNELSETUP(adc_channel);
    // data_array[1] = flags;

    // SPI.transfer(data_array, 2);
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
    
    // Not sure why we do this...
    digitalWrite(_cs, LOW);

    //read bytes of channel data register (16 bit mode)
    upper = SPI.transfer(0);
    middle = SPI.transfer(0);
    lower = SPI.transfer(0);
    
    // Not sure why we do this either...
    digitalWrite(_cs, HIGH);

    SPI.endTransaction();

    // Convert
    int result = ((upper&0xff)<<10 | (middle&0xff) << 2 | (lower&0xff) >> 6);
    
    return result;
}