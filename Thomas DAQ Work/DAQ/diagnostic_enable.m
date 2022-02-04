
serport = serialport("COM7", 9600);

command = 3; % For interface check

enable = 0; % 0 = disable, 1 = enable

send_data = zeros(1, 16, 'uint8');
send_data(1) = bitor(bitshift(command, 4), enable);

write(serport, send_data, "uint8");

delete(serport);