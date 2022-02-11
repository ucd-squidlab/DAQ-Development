serport = serialport("COM7", 9600);

command = 4; % Which command

data0 = 0;
data1 = 0;

send_data = zeros(1, 16, 'uint8');
send_data(1) = bitor(bitshift(command, 4), data0);
send_data(2) = bitand(data1,0xFF);

write(serport, send_data, "uint8");

delete(serport);