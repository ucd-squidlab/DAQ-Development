
serport = serialport("COM7", 9600);
voltMax = 10;

% Send command to get an ADC reading
command = 2;
send_data = zeros(1, 16, 'uint8');
send_data(1) = bitshift(command, 4);
write(serport, send_data, "uint8"); % Send command
read_data = read(serport, 3, 'uint8'); % Read response
data = read_data;

val = bitshift(data(1),10) ...
    + bitshift(data(2),2) + bitshift(data(3),-6);

voltage = val/(2^17)*voltMax;
if (bitand(read_data(1), 0x80) ~= 0)
 voltage = voltage-voltMax*2;
end
voltage

% Max voltage is represented as 131072
output = val / 131072 * voltMax;
%Check for 2's complement
if bitand(data(1),0x80) ~= 0
    output = output - voltMax*2;
end

binStr = dec2bin(val, 18);

val2 = bitshift(data(1),16) ...
       + bitshift(data(2),8) + bitshift(data(3),0);
binStr2 = dec2bin(val2);

dec2hex(bitshift(val, 0));

delete(serport);