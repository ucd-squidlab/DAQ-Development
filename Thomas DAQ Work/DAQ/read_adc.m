
delete(serport)
serport = serialport("COM7", 9600);

command = 2;

data = uint16(3276.8*(voltage + 10));
send_data = zeros(1, 16, 'uint8');
send_data(1) = bitshift(command, 4);
write(serport, send_data, "uint8");

read_data = read(serport, 3, 'uint8');
data = read_data
%val = bitshift(read_data(1), 16) ...
%+ bitshift(read_data(2), 8) ...
%+ bitshift(read_data(3), 0);
val = bitshift(data(1),10) ...
    + bitshift(data(2),2) + bitshift(data(3),-6);

voltage = val/(2^18)*20.0;
if (bitand(read_data(1), 0x80) ~= 0)
 voltage = voltage-20;
end

output = val / 13107.2;
%Check for 2's complement
if bitand(data(1),0x80) ~= 0
    output = output - 20;
end

binStr = dec2bin(val, 18);

dec2hex(bitshift(val, 0))

delete(serport)