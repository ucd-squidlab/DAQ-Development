#include "SPI.h"
int led=13;
int adc_cs=46;
int dac_cs=22;
int busy=48;
int reset=50;
int convst=52;
long fft[50000];
byte buf[200000];

SPISettings adc(60000000, MSBFIRST, SPI_MODE2);
SPISettings dac(2000000, MSBFIRST, SPI_MODE1);

void setup() {
  long output;
  unsigned long cputime, cputime2,wait;
  Serial.begin(250000);
  pinMode(led,OUTPUT);
  pinMode(reset, OUTPUT);
  pinMode(busy, INPUT);  //Data ready pin for the ADC.  
  pinMode(convst,OUTPUT);
  pinMode(adc_cs, OUTPUT);
  pinMode(dac_cs, OUTPUT);
  SPI.begin();
  SPI.beginTransaction(dac);
  digitalWrite(dac_cs, LOW);
  SPI.transfer(0x14);
  SPI.transfer(0xC0);
  SPI.transfer(0x00);
  digitalWrite(dac_cs, HIGH);
  SPI.endTransaction();
  digitalWrite(reset,HIGH);
  digitalWrite(reset,LOW);
  delayMicroseconds(100);
  SPI.beginTransaction(adc);
  digitalWrite(adc_cs, LOW);
  SPI.transfer(0x02);
  SPI.transfer(0x18);
  digitalWrite(adc_cs, HIGH);
  SPI.endTransaction();
  delayMicroseconds(100);
  wait = 0;
  cputime2 = micros();
  for (int i = 0;i < 50000;i++){
    while(wait>micros()){}
    cputime = micros();
    wait = cputime+99;
    fft[i] = getConversionData();
  }
  cputime = micros();
  fftToBuf();
  Serial.write(buf,40000);
  Serial.println(micros()-cputime);
}

long getConversionData(){
  byte one, two, three;
  long combined;
  digitalWrite(convst,LOW);
  digitalWrite(convst,HIGH);
  delayMicroseconds(5);
  SPI.beginTransaction(adc);
  digitalWrite(adc_cs, LOW);
  one=SPI.transfer(0x00);
  two=SPI.transfer(0x00);
  three=SPI.transfer(0x00);
  digitalWrite(adc_cs, HIGH);
  SPI.endTransaction();
  combined = ((one&0xff)<<10 | (two&0xff) << 2 | (three&0xff) >> 6);
  return combined;
}

void fftToBuf(){
  for (int i = 0;i < 10000;i++){
    buf[i*4]=((fft[i]>>24)&0xFF);
    buf[i*4+1]=((fft[i]>>16)&0xFF);
    buf[i*4+2]=((fft[i]>>8)&0xFF);
    buf[i*4+3]=(fft[i]&0xFF);
  }
}

void loop() {
  // put your main code here, to run repeatedly:

}
