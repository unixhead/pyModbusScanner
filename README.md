# pyModbusScanner
Basic GUI for probing modbus TCP data

Makes use of pyModbusTCP for all the hard work: https://github.com/sourceperl/pyModbusTCP

GUI components use the dearpygui framework: https://github.com/hoffstadt/DearPyGui

# Usage
Requires pyModbusTCP and dearpygui to be installed with: 
`sudo pip install dearpygui pyModbusTCP`

Download the files pyModbusScanner-v0.2.py and SourceSans3-Regular.otf into the same directory, then run with:

`python pyModbusScanner`

Fire it up, enter IP/port for modbus service, click "test connection" and verify that the status indicator goes green and says "Connected". 
Then enter max/min values for either coils, registers or input registers and hit the relevant "scan" button, results should appear in the box beneath.

Debug info gets dumped into the console so if it goes wrong hten there may be some hints in the terminal you launched it from. 

License is Beerware

# Test Environment
If you need a modbus server to test with then grab Control Things Linux from here: https://www.controlthings.io/
Load up ModbusPal, hit "load" and open the included VoltageRegulator.xmpp (should be in /home/control/samples/Simulators/ModbusPal), click Run and that'll give you a Modbus Service to poke at. Output should be similar to that below.



# Screenshot
![name-of-you-image](https://raw.githubusercontent.com/unixhead/pyModbusScanner/main/ss.png)
