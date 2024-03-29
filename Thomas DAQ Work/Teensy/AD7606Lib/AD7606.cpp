/*
Version 22.03.1
*/

#include <Arduino.h>
// #include <string.h>
#include "SPI.h"
#include "AD7606.h"


//All pages reference AD7606C-18 Data Sheet Rev A

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
#define ADDR_GAINCH1                  0x09
#define ADDR_GAINCH2                  0x0A
#define ADDR_GAINCH3                  0x0B
#define ADDR_GAINCH4                  0x0C

#define ADDR_GAIN(ch) (0x09+ch)


// Dout format: number of lines used for clocking out data via SPI.
// This library assumes access to only line 0.
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
void AD7606::SetupAD7606(int cs, int rst, int busy, int convst, int baudrate) {
    // Pin IDs
    _cs = cs; // Chip select
    _rst = rst; // Reset
    _busy = busy; // Busy (not currently used)
    _convst = convst; // Conversion start
    
    // Initial configuration
    status_header = ext_os_clock = dout_format = operation_mode = 0;
    
    // Keep track of what mode we're in right now. Default: ADC mode
    ADCMode = true;
    diagnosticMode = false;
    
    
    adc_settings = SPISettings(baudrate, MSBFIRST, SPI_MODE2);
    
    
    //set bit order for ADC
    // SPI.setBitOrder(_cs, MSBFIRST);
    //set clock divider for DAC
    //SPI.setClockDivider(_cs, SPI_CLOCK_DIV64);
    //set data mode for dac
    // SPI.setDataMode(_cs, SPI_MODE2);

    //SPI.usingInterrupt(_rdy);
    
    
    // Set pin modes
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
    
    // Initialize all eight ADC readings to zero
    memset(adc_reading, 0, sizeof(adc_reading));
    
    // Whether the saved data corresponds to the last conversion
    uptodate = false;
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

void AD7606::FullReset() {
    digitalWrite(_rst, HIGH);
    delayMicroseconds(5);
    digitalWrite(_rst, LOW);
}

// Write data to a register
// *** Not tested yet
void AD7606::RegisterWrite(uint8_t reg, uint8_t data) {
    if (ADCMode) {
        RegisterModeEnable();
    }
    
    SPI.beginTransaction(adc_settings);
    digitalWrite(_cs, LOW);
    // First byte is action type | register ID
    SPI.transfer(WRITE | reg);
    // Second byte is data
    SPI.transfer(data);
    digitalWrite(_cs, HIGH);
    SPI.endTransaction();
    
    ADCModeEnable();
}

// *** Not tested yet
// This function sets the fine gain for the ADC.
// Currently, it looks like it's written to only change the gain for
// channel 0.
// Need to check datasheet and see if everything here is correct.
void AD7606::GainCalibration(uint8_t val) {
    // Pick only the last 6 bits of the gain value
    val = val & 0x3f;
    // Write to the register
    uint8_t reg = ADDR_GAIN(0);
    RegisterWrite(reg, val);
}

// Interface check mode: the ADC will return fixed, predictable
// values for each channel. This allows us to troubleshoot
// the interface.
void AD7606::InterfaceCheckMode(bool enable) {
    if (ADCMode) {
        RegisterModeEnable();
    }
    
    // Bit 7 is for interface check
    // 1 = enable, 0 = disable
    uint8_t code = 1 << 7;
    if (!enable) {
        code = 0;
    }
    
    // Diagnostic register: 0x21
    uint8_t data[2] = {WRITE | 0x21, code};
    
    // Send the new register data
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
    // Combine the configuration data
    uint8_t config_data = status_header | ext_os_clock | dout_format | operation_mode;
    
    // Send data to the ADC
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

// High sample rate = splitting the 8 channels over all 8 doutx lines.
// This means that only a single channel is transmitted over a single
// line.
// I have not been able to find a method for reading the 8 channels
// simultaneously on different lines. So the only reason this function
// is useful is that it means we only need to read a single channel (24 bits)
// from the SPI line, instead of all 8 channels.
// But technically, this function is unnecessary. When all 8 channels are sent
// on a single line, we could just read the first 24 bits and then stop.
// When the next ADC conversion is complete, the ADC will start over again
// with channel 0. So if we're interested in just channel 0, we could keep
// the ADC in DOUTX1 mode with all 8 channels being sent on line 0. We read
// 24 bits from line 0, then we trigger a conversion, then we read 24 more bits
// from line 0.
// The problem is that, if we somehow forget the result for channel 0 and need
// to re-read that channel before starting a new conversion, then we have to
// read channels 1-7 before we get back to channel 0. But if we can guarantee
// that this will never happen, then we don't need to split
// the 8 channels over different lines.
void AD7606::HighSampleRate(bool enable) {
    if (dout_format != DOUTX8 and enable) {
        // If we're not in fast mode already
        dout_format = DOUTX8;
        UpdateConfiguration();
    } else if (dout_format != DOUTX1 and !enable) {
        // If we're currently in fast mode
        dout_format = DOUTX1;
        UpdateConfiguration();
    }
    ADCModeEnable();
}

// Quickly get conversion data for channel 0. NOTE: Assumes that
// we are already in fast mode, and adds the data to an array in-place.
void AD7606::GetConversionDataFast(uint8_t (& result)[3]) {
    // Clear the array; this is necessary because a few lines later
    // we'll be sending it over SPI, so it needs to contain only zeros
    result[0] = 0;
    result[1] = 0;
    result[2] = 0;
    SPI.beginTransaction(adc_settings);
    digitalWrite(_cs, LOW);
    // Send the array over SPI and read the conversion result into the same array
    SPI.transfer(result, 3);
    digitalWrite(_cs, HIGH);
    SPI.endTransaction();
}

// Get conversion data for a particular channel.
// If the channel we're reading is NOT channel 0, then we need to
// combine all of the channel results onto line 0 so we can access them.
// (Note: with the current implementation, the transfer time slows by a factor of 8.)
// TODO: Modify this so that all of the results are returned. Or
// maybe take an array of channels, and modify the array in-place
// with the channel conversion results.
uint32_t AD7606::GetConversionData(uint8_t channel) {
    if (!ADCMode) {
        ADCModeEnable();
    }
    
    // If the channel is not channel 0, disable the high sample rate (this
    // will combine all of the channel results on line 0 so we can access them).
    if (channel > 0 && dout_format != DOUTX1) {
        HighSampleRate(false);
    }
    
    // The adc_reading array contains the result for different channels. Reset it to zero
    memset(adc_reading, 0, sizeof(adc_reading));
    
    uint32_t result = 0;
    uint8_t upper, middle, lower;
    
    /*** Below: SLIGHTLY FASTER VERSION OF TRANSFER. Not tested yet. ***/
    // How many bytes we need to receive over SPI. If the ADC outputs 1 channel
    // per line, then we only need 3 bytes.
    /*
    uint8_t bytenum = 3;
    if (dout_format == DOUTX1) {
        bytenum = 18;
    }
    
    uint8_t position = channel*18; // Which bit to start on
    uint8_t startbyte = position/8; // Which byte this corresponds to
    uint8_t startbit = position % 8; // What position is bit 1 within the byte
    
    uint8_t data[bytenum] = {0};
    
    // Transfer data
    SPI.beginTransaction(adc_settings);
    digitalWrite(_cs, LOW);
    SPI.transfer(data, bytenum);
    digitalWrite(_cs, HIGH);
    SPI.endTransaction();
    
    upper = (data[startbyte] << startbit) | (data[startbyte+1] >> (8-startbit));
    middle = (data[startbyte+1] << startbit) | (data[startbyte+2] >> (8-startbit));
    lower = (data[startbyte+2] << startbit) | (data[startbyte+3] >> (8-startbit));
    */
    
    /*** Below: SLOW VERSION OF TRANSFER. ***/
    // Transfer each channel using 3 bytes. This works because
    // flipping the chip select pin causes the ADC to start over
    // with the channel it was sending.
    
    uint8_t total_transfer_num = 1; // How many channels we'll need to read from the line
    if (dout_format == DOUTX1) {
        total_transfer_num = 8;
    }
    
    SPI.beginTransaction(adc_settings);
    // Read the channels
    for (int i = 0; i < total_transfer_num; ++i) {
        digitalWrite(_cs, LOW);
        // Three bytes transferred from ADC
        upper = SPI.transfer(0);
        middle = SPI.transfer(0);
        lower = SPI.transfer(0);
        // Save the result for this channel
        adc_reading[i] = ((upper&0xff)<<16 | (middle&0xff) << 8 | (lower&0xff));
        digitalWrite(_cs, HIGH);
    }
    SPI.endTransaction();
    
    // Select the channel of interest
    result = adc_reading[channel];
    
    /** Below: Original version, only reads channel 0 **/
    /*
    SPI.beginTransaction(adc_settings);
    digitalWrite(_cs, LOW);
    upper = SPI.transfer(0);
    middle = SPI.transfer(0);
    lower = SPI.transfer(0);
    digitalWrite(_cs, HIGH);
    SPI.endTransaction();
    
    // Convert
    result = ((upper&0xff)<<16 | (middle&0xff) << 8 | (lower&0xff));
    */
    
    return result;
}

// uint32_t AD7606::ReadConversionResult