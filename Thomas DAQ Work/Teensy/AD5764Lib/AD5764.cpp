#include "Arduino.h"
#include "SPI.h"
#include "AD5764.h"
// **** TODO: Update DAC to use 2's complement!!! ****
// This will make it so that the DAC powers up at 0 V instead of -10 V.



//All tables references AD5764 Data Sheet Rev F
//Table 9: Defines for the input shift regsiter bit map, designed to be OR'd together to create a valid input for the AD5764

//Read/Write bit (R, W), Table 10
#define READ  1 << 7
#define WRITE 0

//Function select bits (REG0, REG1, REG2), Table 10
#define FUNCTION_REG  0 << 3
#define DATA_REG      2 << 3
#define COURSE_REG    3 << 3
#define FINE_REG      4 << 3
#define OFFSET_REG    5 << 3

//Course gain options, Table 15
#define COURSE_GAIN_0 0
#define COURSE_GAIN_1 1
#define COURSE_GAIN_2 2

//Function select bits (sets [A2, A1, A0], when FUNCTION_REG selected), Table 11
#define NOP 0
#define LOCAL_GROUND_OFFSET_ADJUST 1
#define CLEAR_DATA  4
#define LOAD_DATA   5

//DAC Reference Voltage
#define VREFIN 5.0

/***  Current coding expecting voltage preconverted, therefore following isn't being used. ***/
//converts a decimal value into a value between 0-65535, so it can be used by the DAC
//max voltage output ±10V (default), set by course gain register
#define CONVERT_VALUE2DAC(vout) ((uint16_t)(16384.0 * ((vout/VREFIN) + 2)))

AD5764::AD5764() { }
AD5764::~AD5764() { }

void AD5764::SetupAD5764(int cs, int ldac, int clr) {
	//assign pin values to class members
	_cs = cs;
	_ldac = ldac;
	_clr = clr;

    
	dac_settings = SPISettings(2000000, MSBFIRST, SPI_MODE1);
    
    
	//setup SPI communication with DAC
	SPI.begin();

	//set pin modes for LDAC and CLR pins
	pinMode(_ldac, OUTPUT);
	pinMode(_clr, OUTPUT);
    pinMode(_cs, OUTPUT);

	//write pin values
	//eval-AD5764 board, LK8 jumper is currently driven (A) (if connected to ground, would be unnecessary) 
	//digitalWrite(_ldac, LOW);    //we will not use LDAC, so it will be driven low, dac will automatically respoind with rising edge of the chip select signal

	//the DAC has a startup reset method, which will automatically clear the DAC on start
	//digitalWrite(_clr, HIGH);    //not going to clear the DAC, must be driven high

	//place DAC into known state ( 0 on all channels )
	SetDataRegister(CONVERT_VALUE2DAC(0), DAC_ALL);
}

//sets the output on the specified DAC channel
//the data word is a value between 0-65535 in Binary encoding
void AD5764::SetDataRegister(uint16_t vout, uint8_t dac_channel) {
	//generate DAC Input Shift Register Bit Map (24bits), Table 9 with data in binary coding (Table 7)
	//using following bits to generate map:
	//WRITE | DATA_REG | DAC_Address | data

	//make an array of bytes to send in MSB first order
	uint8_t data_array[3];
	data_array[0] = WRITE | DATA_REG | dac_channel;
	data_array[1] = (vout & 0xFF00) >> 8;
	data_array[2] = (vout & 0x00FF);
    
    //uint16_t vout_daq = 16384.0 * ((vout/VREFIN) + 2);
    
    
	//transfer the data to the DAC
    SPI.beginTransaction(dac_settings);
    digitalWrite(_cs, LOW);
	SPI.transfer(data_array, 3);
    SPI.endTransaction();
    digitalWrite(_cs, HIGH);
}

// Set the fine gain. Each gain step will change the output
// voltage at -10V by 1/2 LSB.
// The gain should be encoded using 2's complement.
// See AD5764 datasheet for more details.
void AD5764::FineGain(uint8_t gain, uint8_t dac_channel) {
    // Pick only the last 6 bits of the gain value
    gain = gain & 0x3f;
    
	//make an array of bytes to send in MSB first order
	uint8_t data_array[3];
	data_array[0] = WRITE | FINE_REG | dac_channel;
	data_array[1] = 0;
	data_array[2] = gain;
    
    // Send to the DAC
    SPI.beginTransaction(dac_settings);
    digitalWrite(_cs, LOW);
	SPI.transfer(data_array, 3);
    SPI.endTransaction();
    digitalWrite(_cs, HIGH);
}

// Set the offset. Each offset step will shift the output
// voltage by 1/8 LSB.
// The offset should be encoded using 2's complement.
// See AD5764 datasheet for more details.
void AD5764::Offset(uint8_t offset, uint8_t dac_channel) {    
	//make an array of bytes to send in MSB first order
	uint8_t data_array[3];
	data_array[0] = WRITE | OFFSET_REG | dac_channel;
	data_array[1] = 0;
	data_array[2] = offset;
    
    // Send to the DAC
    SPI.beginTransaction(dac_settings);
    digitalWrite(_cs, LOW);
	SPI.transfer(data_array, 3);
    SPI.endTransaction();
    digitalWrite(_cs, HIGH);
}