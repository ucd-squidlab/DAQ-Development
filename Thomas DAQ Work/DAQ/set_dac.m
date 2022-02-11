
serport = serialport("COM7", 9600);

dac = 0;
voltage = 1;

vmax = 10;


data = uint16(32768/vmax*(voltage + vmax));
send_data = zeros(1, 16, 'uint8');
send_data(1) = bitor(bitshift(0, 4), dac);
send_data(2) = bitshift(bitand(data,0xFF00),-8);
send_data(3) = bitand(data,0x00FF);
write(serport, send_data, "uint8");

delete(serport)