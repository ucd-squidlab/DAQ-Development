
serport = serialport("COM7", 9600);

command = 3;

voltage = 1

data = uint16(3276.8*(voltage + 10));
send_data = zeros(1, 16, 'uint8');

send_data(1) = bitshift(command, 4);
write(serport, send_data, "uint8");

delete(serport);