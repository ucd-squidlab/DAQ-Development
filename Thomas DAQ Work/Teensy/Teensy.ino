/** Version 22.04.3
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
 *    slew rate has been capped, because voltage updates will not be
 *    instantaneous so the host computer may want to be alerted after
 *    the process is complete. A response code of 0 means success.
 * 
 * 
 * 1. Begin ADC Conversion
 *    Code: 1
 *    
 *    Trigger an ADC conversion.
 *    
 *    
 * 2. Get ADC Result
 *    Code: 2
 *    
 *    Read the result of the last conversion and
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
 * 5. Initiate a fast sample collection
 *    Code: 5
 *    data[1]: Sampling period, in microseconds
 *    data[2-4]: Total number of samples
 *    
 *    Collect a bunch of samples at a high sample rate and
 *    save in a local buffer. When sampling is complete, the
 *    data may requested using a different command.
 *    
 *    
 * 6. Collect fast sample results
 *    Code: 6
 *    
 *    Returns the stored data from the fast sample collection.
 *    Note that some of the data may be dropped; the host is reponsible
 *    for verifying completeness and re-requesting the data if necessary.
 * 
 */
//DAC library header
#include "AD5764.h"
//ADC library header
#include "AD7606.h"
//Arduino SPI library header
#include <SPI.h>

#include <algorithm>

using namespace std;

//instance of the AD5764 class ( DAC )
AD5764 dac;
//instance of the AD7606 class ( ADC )
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

// Stuff for the fast-sampling feature
IntervalTimer fast_sample_timer;
byte fast_samples[300000];
int sample_count = 0; // How many samples sent so far
int target_count = 0; // Target number of samples
// Whether the DAQ is actively sampling right now
bool active_sampling = false;


bool LEDState = false;

// How long it should take to change an output voltage, in microseconds per step.
// NOTE: This feature assumes that a value of 0x0000 corresponds
// to the minimum possible voltage and 0xFFFF corresponds to the
// maximum voltage. If the DAC library is changed, then
// the feature may need to be rewritten.
uint16_t DACDeltaT[4] = {1, 0, 0, 0};
// Step size when changing the DAC output voltage, in LSB
// (Same for all channels)
uint8_t DACStepSize = 1;


// Current state of DAC
// *** NOT IMPLEMENTED ***
uint16_t DACVout[4] = {1<<15};

void setup() {
    //begin serial communication
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
    SetDAC(1<<15, 0);
    SetDAC(1<<15, 1);
    SetDAC(1<<15, 2);
    SetDAC(1<<15, 3);
}

// Take a single sample.
// This should be used with an IntervalTimer to get a bunch
// of evenly-spaced samples
void GetFastSample() {
  adc.StartConversion();
  
  // Wait for the conversion to finish
  delayMicroseconds(1);
  
//  uint32_t adc_response = adc.GetConversionData(0);
//  fast_samples[sample_count*3] = (adc_response >> 16) & 0xFF;
//  fast_samples[sample_count*3 + 1] = (adc_response >> 8) & 0xFF;
//  fast_samples[sample_count*3 + 2] = (adc_response) & 0xFF;
  
  uint8_t adc_response[3] = {0};
  // Get unprocessed conversion data and store it in adc_response
  adc.GetConversionDataFast(adc_response);
  // Transfer conversion data into a buffer
  fast_samples[sample_count*3] = adc_response[0];
  fast_samples[sample_count*3 + 1] = adc_response[1];
  fast_samples[sample_count*3 + 2] = adc_response[2];
  // Increment the total number of samples
  ++sample_count;
  // If we've reached the target, stop sampling
  if (sample_count >= target_count) {
    fast_sample_timer.end();
    active_sampling = false;
    LEDToggle();
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


// Get the result from last conversion and send it to host over USB serial
void GetADCResult(uint8_t channel) {
//    adc.StartConversion();
//    delayMicroseconds(1000);

    // Get processed conversion data
    uint32_t adc_response = adc.GetConversionData(channel);
    
    byte adc_data[3];
    adc_data[0] = (adc_response >> 16)&0xFF;
    adc_data[1] = (adc_response >> 8)&0xFF;
    adc_data[2] = (adc_response)&0xFF;

    Serial.write(adc_data, 3);
}

// Set the DAC output on channel `channel` to voltage `vout`
// where `vout` is encoded assuming that 0x0000 = -10V and
// 0xFFFF = 10V
int SetDAC(uint16_t vout, uint8_t channel) {
  // Get the deltaT for each step
  uint16_t deltaT = 0;

  // If all four channels need to be set, then
  // set them individually instead of all at once
  // to make sure the max slew rate is not exceeded
  // on any channel
  if (channel == 4) {
    SetDAC(vout, 0);
    SetDAC(vout, 1);
    SetDAC(vout, 2);
    SetDAC(vout, 3);
    return 0;
  // Get time delay for each step
//    deltaT = *std::max_element(DACDeltaT, DACDeltaT+4);
//    if (deltaT > 0) {
//      // Abort if there are slew rate restrictions on any channels.
//      return 1;
//    }
  } else {
    // Get the maximum slew rate
    deltaT = DACDeltaT[channel];
  }

  // Set the voltage for this channel
  if (deltaT == 0) {
    // If there is no maximum slew rate, change the voltage immediately 
    DACVout[channel] = vout;
    dac.SetDataRegister(vout, channel);
  } else {
    // There is a maximum slew rate, so we need to change gradually.
    
    // Direction (increasing or decreasing voltage):
    int dir = 2*(vout > DACVout[channel]) - 1; // 1 if increasing, -1 if decreasing
    
    bool complete = false;
    while(!complete) {
      // Step the voltage
      DACVout[channel] += dir*DACStepSize;
      // Check whether we've reached (or passed) the goal yet
      if (dir*DACVout[channel] >= dir*vout) {
        DACVout[channel] = vout; // Make sure we don't overshoot
        complete = true;
      }
      // Update the voltage
      dac.SetDataRegister(DACVout[channel], channel);
      // Wait for the delay period before moving on to the next step
      delayMicroseconds(deltaT);
    }
  }
  // 0 = success
  return 0;
}


//wait for a valid 16 byte data stream to become available
void loop() {
    // Copy the active_sampling variable. The active sampling
    // functionality is asynchronous and could interrupt the
    // main program at any time, so we need to disable interrupts
    // temporarily so that the variable won't be overwritten during
    // the copy.
    bool disable;
    noInterrupts();
    disable = active_sampling;
    interrupts();

    // If we're actively sampling, we shouldn't do anything else...
    if (disable) {
      return;
    }
    
    //if Serial.available() % 16 != 0 after a communication is completed, then the Arduino will not process
    //the bitstream properly, the fastest way to fix this is a restart, the input stream can also be flushed with data
    //until Serial.available() % 16 == 0.
    if (Serial.available() >= 16 && !disable) {
        //read 16 bytes of serial data into a data buffer
        unsigned char data[16];
        Serial.readBytes(data, 16);

        //get function code (upper 4 bits from first data byte)
        uint8_t fnc = data[0] >> 4;

        // Remove function code from first byte
        data[0] = data[0] & 0xF;

        // We need to declare these outside of the switch statement.
        // If we declare inside the switch statement, bugs happen.
        bool enable;
        unsigned char response_code;

        // Branch based on function code
        // 
        switch (fnc) {                
            case 0:
                response_code = 0;
                // Change the voltage on the passed DAC channel to the passed voltage 
                response_code = SetDAC((data[1] << 8) | data[2], data[0] & 0x7);

                if (data[3] > 0) {
                  Serial.write(response_code);
                }
                break;

            case 1:
                // Begin ADC conversion
                adc.StartConversion();
                break;

            case 2:
                // Get result of last conversion, send result over serial
                GetADCResult(data[0]);
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
                // Get a set of fast samples from channel 0
                // Turn on the high sampling rate between the ADC and
                // the Teensy (this means that only
                // a single channel will be sent on each Doutx line).
                adc.HighSampleRate(true);

                // Reset total samples
                sample_count = 0;
                // Set target number of samples (limited to 100000)
                target_count = (data[2] << 16) + (data[3] << 8) + (data[4]);
                target_count = min(100000, target_count);
                // Begin sampling
                active_sampling = true;
                LEDToggle();
                fast_sample_timer.begin(GetFastSample, data[1]);
                break;

            case 6:
                // Send fast sample result over serial to host. Some
                // of these bytes may be dropped during transmission, so the
                // host computer should confirm that the packet is the correct
                // size, and if not, re-request the data. In the future
                // it may be worth splitting this into smaller packets
                // so that only the packet with missing data needs to be
                // re-transmitted.
                if (sample_count > 0) {
                  Serial.write(fast_samples, sample_count*3);
                }
                break;
                
            default:
                LEDToggle();
        }
    }
}
