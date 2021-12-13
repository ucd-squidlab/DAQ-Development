
serport = serialport("COM7", 9600)


data = uint16(3276.8*(1.5 + 10));
send_data = zeros(1, 16, 'uint8');
send_data(1) = bitor(bitshift(0, -4), bitshift(0, -2));
send_data(2) = bitshift(bitand(data,0xFF00),-8);
send_data(3) = bitand(data,0x00FF);
write(serport, send_data, "uint8");

delete(serport)