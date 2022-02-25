array = [];
count = 21;
startv = -10;
endv = 10;

vrange = endv - startv;
for i=1:count
    voltage = startv + (i-1)*vrange/(count-1);
    array(i, 1) = voltage;
    set_dac;
    read_adc;
    %voltage = voltage*0.95+0.05;
    array(i, 2) = voltage*gain;
end

array