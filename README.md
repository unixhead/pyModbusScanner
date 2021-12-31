# pyModbusScanner
Basic GUI for probing modbus TCP data

Makes use of pyModbusTCP for all the hard work: https://github.com/sourceperl/pyModbusTCP

GUI components use the dearpygui framework: https://github.com/hoffstadt/DearPyGui

# Usage
Needs Python 3.x for the GUI library, if you're having a problem running it then drop me a line and will see if I can work out what's up. Only tested on Mint 20 at this point. 

Requires pyModbusTCP and dearpygui to be installed with: 
`sudo pip install dearpygui pyModbusTCP`

Download the files pyModbusScanner-v0.3.py and SourceSans3-Regular.otf into the same directory, then run with:

`python pyModbusScanner-v0.3.py`

Fire it up, enter IP/port for modbus service, click "test connection" and verify that the status indicator goes green and says "Connected". 
Then enter max/min values for either coils, registers or input registers and hit the relevant "scan" button, results should appear in the box beneath. 

Debug info gets dumped into the console so if it goes wrong then there may be some hints in the terminal you launched it from. 

License is Beerware

# Modbus Scanning Notes
Start with small port ranges, especially if hitting a PLC with low resources! I should probably include a delay setting in a future version.

Coil scanning will just show the address (0-65536) of any coils that are set to 1 rather than 0 as they're boolean values, scanning the registers will output the values held in those registers. 

The values are fairly meaningless on their own as you need the context of what they represent and that isn't directly detailed in the protocol responses, these  are just addresses and values. There's no information in the protocol responses that might indicate whether that value is a button status, pressure reading, kitkats remaining in stock, number of games of tictactoe that have been won or any other possible value.

Registers are 16 bit, but some implementations may use 32 bit by joining two together. This software will just show two separate 16 bit values. 

It may be possible to fingerprint modbus devices and provide more useful information, might be a future update!

Spec is here: https://modbus.org/docs/Modbus_Messaging_Implementation_Guide_V1_0b.pdf


# Test Environment
One option is to run the Modbus Server GUI that I'm working on: https://github.com/unixhead/pyModbusServerGUI

Another is to use the excellent Control Things Linux from here: https://www.controlthings.io/
Load up ModbusPal, hit "load" and open the included VoltageRegulator.xmpp (should be in /home/control/samples/Simulators/ModbusPal), click Run and that'll give you a Modbus Service to poke at. Output should be similar to that below.



# Screenshot
![name-of-you-image](https://raw.githubusercontent.com/unixhead/pyModbusScanner/main/ss.png)
