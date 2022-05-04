The DAC data are pairs of voltages. The first value in each pair represents the target output voltage. The second value is the actual output voltage.

The DAQ is skewing the values by:
Gain: 0.999582
Offset: +0.304 mV

To correct this, we need to apply:
Gain: 1.000418
Offset: -0.304 mV (= 0.996 LSB)
