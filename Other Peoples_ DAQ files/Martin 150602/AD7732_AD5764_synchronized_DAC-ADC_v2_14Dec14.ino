//Ardunio *DUE(*code for controlling EVAL-AD7732 ADC 
#include "SPI.h" // necessary library for SPI communication

int adc=52; //The SPI pin for the ADC
int dac=4;  //The SPI pin for the DAC
int ldac=6; //Load DAC pin for DAC. Make it LOW if not in use. 
int clr=5;  // Asynchronous clear pin for DAC. Make it HIGH if you are not using it
int reset=51; //Reset on ADC
int drdy=50; // Data is ready pin on ADC
int led=13;//Used for trouble shooting; connect an LED between pin 53 and GND\
int debug=10;

void setup()
{
  Serial.begin(115200);
  pinMode(ldac,OUTPUT);   
  digitalWrite(ldac,LOW); //Load DAC pin for DAC. Make it LOW if not in use. 
  pinMode(clr, OUTPUT);
  digitalWrite(clr,HIGH); // Asynchronous clear pin for DAC. Make it HIGH if you are not using it
  pinMode(reset, OUTPUT);
  pinMode(drdy, INPUT);  //Data ready pin for the ADC.  
  pinMode(led, OUTPUT);  //Used for blinking indicator LED

  digitalWrite(reset,HIGH);  digitalWrite(led,LOW); digitalWrite(reset,LOW);  digitalWrite(led,HIGH); delay(5);  digitalWrite(reset,HIGH);  digitalWrite(led,LOW);//Resets ADC on startup.  

  SPI.begin(adc); // wake up the SPI bus for ADC
  SPI.begin(dac); // wake up the SPI bus for ADC
  SPI.begin(debug); // wake up the SPI bus for ADC
  
  SPI.setBitOrder(adc,MSBFIRST); //correct order for AD7732.
  SPI.setBitOrder(dac,MSBFIRST); //correct order for AD5764.
  SPI.setBitOrder(debug,MSBFIRST); //correct order for AD5764.
    
  SPI.setClockDivider(adc,84);  //This can probably be sped up now that the rest of the code is better optimized. Limited by ADC
  SPI.setClockDivider(dac,84);  //This can probably be sped up now that the rest of the code is better optimized. Limited by ADC\
  SPI.setClockDivider(debug,84);  //This can probably be sped up now that the rest of the code is better optimized. Limited by ADC
  SPI.setDataMode(adc,SPI_MODE3); //This should be 3 for the AD7732
  SPI.setDataMode(dac,SPI_MODE1); //This should be 1 for the AD5764
  SPI.setDataMode(debug,SPI_MODE1); //This should be 1 for the AD5764
}

void blinker(int s){digitalWrite(led,HIGH);delay(s);digitalWrite(led,LOW);delay(s);}
void sos(){blinker(50);blinker(50);blinker(50);blinker(500);blinker(500);blinker(500);blinker(50);blinker(50);blinker(50);}

void waitDRDY() {while (digitalRead(drdy)==HIGH){}}

void resetADC() //Resets the ADC, and sets the range to default +-10 V 
{
  digitalWrite(led,HIGH);digitalWrite(reset,HIGH);digitalWrite(reset,LOW);digitalWrite(reset,HIGH);
  SPI.transfer(adc,0x28);
  SPI.transfer(adc,0);
  SPI.transfer(adc,0x2A);
  SPI.transfer(adc,0);
}

void talkADC(byte DB[7])
{
  int comm;
  comm=SPI.transfer(adc,DB[1]);
  Serial.println(comm);
  Serial.flush();
}

void writeADCConversionTime(byte DB[7])
{
  int adcChannel=DB[0]&3;
  byte cr;
  switch (adcChannel)
  {   
    case 1:
    SPI.transfer(adc,0x30);
    SPI.transfer(adc,DB[1]);
    delayMicroseconds(100);
    SPI.transfer(adc,0x70);
    cr=SPI.transfer(adc,0); //Read back the CT register
    Serial.write(cr);
    blinker(59);
    break;
    
    case 2:
    SPI.transfer(adc,0x32);
    SPI.transfer(adc,DB[1]);
    delayMicroseconds(100);
    SPI.transfer(adc,0x72);
    cr=SPI.transfer(adc,0); 
    Serial.write(cr);
    blinker(59);blinker(59);
    break;
    
    default:
    blinker(50);blinker(50);blinker(50);blinker(50);blinker(50);blinker(50);
    break;
}

}

void getSingleReading(int adcchan)
{Serial.flush();
  int statusbyte=0;
  byte o2;
  byte o3;
  int ovr;
  switch (adcchan)
  {
    case 0:
//    blinker(100);
    SPI.transfer(adc,0x38);
    SPI.transfer(adc,0x48);
    waitDRDY();
    SPI.transfer(adc,0x48);
    statusbyte=SPI.transfer(adc,0);
    o2=SPI.transfer(adc,0);
    o3=SPI.transfer(adc,0);
    ovr=statusbyte&1;
    switch (ovr)
    {
      case 0:
      Serial.write(o2);
      Serial.write(o3);
      break;
      
      case 1:
      Serial.write(byte(128));
      Serial.write(byte(0));
      break;   
    }
    break;
    
    case 1:
    SPI.transfer(adc,0x3A);
    SPI.transfer(adc,0x48);
    waitDRDY();
    SPI.transfer(adc,0x4A);
    statusbyte=SPI.transfer(adc,0);
    o2=SPI.transfer(adc,0);
    o3=SPI.transfer(adc,0);
    ovr=statusbyte&1;
    switch (ovr)
    {
      case 0:
      Serial.write(o2);
      Serial.write(o3);
      break;
      
      case 1:
      Serial.write(byte(128));
      Serial.write(byte(0));
      break;   
    }
    break; 
    
    default:
//    blinker(100);blinker(1000);blinker(100);blinker(100);
    break;
  }

}

void readADC(byte DB)
{
int adcChannel=DB&3;
switch (adcChannel)
{case 0:
break;
case 1:
getSingleReading(0);
break;
case 2:
getSingleReading(1);
break;
case 3:
getSingleReading(0);
delayMicroseconds(50);
getSingleReading(1);
break;
default:  
break;
}
}

int twoByteToInt(byte DB1,byte DB2) // This gives a 16 bit integer (between +/- 2^16)
{return ((int)((DB1<<24)| DB2))>>16;
}

int intToTwoByteDB1(int s) //needs 32bit style integer representation of actual 16 bit number
{return ((s>>8)&0xFF);}
int intToTwoByteDB2(int s)
{return (s&0xFF);}

void dacDataSend(int ch, byte DB1,byte DB2)
{SPI.transfer(dac,16+ch,SPI_CONTINUE);
SPI.transfer(dac,DB1,SPI_CONTINUE);
SPI.transfer(dac,DB2);}

void autoRamp(byte DB[7])
{
int v1=twoByteToInt(DB[1],DB[2]);
int v2=twoByteToInt(DB[3],DB[4]);
int nSteps=(DB[5]);
int b1;
int b2;
int dacChannel=(DB[0]>>2)&3;
for (int j=0; j<nSteps;j++)
{
b1=intToTwoByteDB1(v1+(v2-v1)*j/(nSteps-1));
b2=intToTwoByteDB2(v1+(v2-v1)*j/(nSteps-1));
dacDataSend(dacChannel,b1,b2);
delayMicroseconds(50);
readADC(DB[0]);
}

}


void writeDAC(byte DB[7])
{
int dacChannel=(DB[0]>>2)&3;
dacDataSend(dacChannel,DB[1],DB[2]);
}


void router(byte DB[7])
{
  Serial.flush();
  switch ((DB[0]>>4) & 15)//uses the first four bits of the first byte to choose what to do.  0000=0=read ADC: 0001=1=Write DAC; 0010=2=autoramp and acquire
  {
    case 0: // Read ADC 
    readADC(DB[0]);
    break;
    
    case 1: // Write DAC **IMPLEMENTED, WORKS
    writeDAC(DB);
    break;
    
    case 2: // Autoramp
    autoRamp(DB);
    break;

    case 3:
    resetADC();
    break;
    
    case 4:
    talkADC(DB);
    break;
    
    case 5: // Write conversion time registers
    writeADCConversionTime(DB);
    break;

    case 6: //Autocalibrate DAC gain and offset adjust NOT IMPLEMENTRED
//    dacAutoCal(DB);
    break;

    default:
    break;
}
}

void loop()
{
  byte bytes[7];
  while (Serial.available()<7) // wait until all data bytes are avaialable
  {
  }
if (Serial.available()) // wait until all three data bytes are avaialable
{
  digitalWrite(led,LOW);
  for (int i=0; i<7; i++) 
  {
    bytes[i] = Serial.read();
    SPI.transfer(debug,bytes[i]);
  }
Serial.flush();
}
router(bytes);
}

