# pyModbusScanner
# Original source: https://github.com/unixhead/pyModbusScanner

# Beerware license

# Uses PyModbusTCP for all the hard work
# https://github.com/sourceperl/pyModbusTCP

#
# Needs dearpygui and pymodbusTCP, run:
# pip install dearpygui pyModbusTCP
#


# Server class abstracts the scanning functions away from the GUI so it can be tweaked.
# Could be in separate file but keeping it together for ease of distribution

from pyModbusTCP.client import ModbusClient

class modbusServer:
    connected = False
    address = "127.0.0.1"
    port = 10502

    def __init__(self):
        self.modbusClientObj = ModbusClient() # reference to the pyModbusTCP object used
        self.coilArray = list()
        

    def connect(self):
        # use the pyModbusTCP library to validate the server address/port & connectivity
        if self.connected == True:
            return True

        self.debugLog("test connection to " + self.address + "/" + self.port)

        if (self.modbusClientObj.host(self.address) == None):
            self.debugLog("Failed to set hostname")
        else:
            self.debugLog("Set hostname")
          
        if (self.modbusClientObj.port(self.port) == None):
            self.debugLog("Failed to set port")
        else:
            self.debugLog("Set port")
           

        if (self.modbusClientObj.open() != True):
            self.debugLog("Connect failed")
        else:
            self.debugLog("connected")
            self.connected = True

        return self.connected


    def connectTest(self):
        return self.connected

    def setAddress(self, data):
        self.address = data

    def setPort(self, data):
        self.port = data


    #Don't need to worry about these as pyModbusTCP sorts them out but ranges are:
    #coils are 0-65536
    #discrete inputs 100001 to 165536
    #input registers 300001 to 365536
    #holding registers 400001 to 465536

    def scanRegisters(self, min, max, dpg = None, progressBar = None):
        self.debugLog("ScanRegisters")

        if self.connected == False:
            self.debugLog("scan called but not connected")
            return False

        max = int(max)
        min = int(min)

        # min > 0 && < max
        # max < 65535
        if max > 65535:
            self.debugLog("Register addresses only go up to 65536")
            return False

        if min < 0 or min > max:
            self.debugLog("Invalid minimum register address")
            return False

        self.registerArray = list()
        self.registerCount = 0

        
        
        for i in range(min,max):
            if i >= 40000 and i <= 49999:
                regContent = self.modbusClientObj.read_holding_registers(i)
            elif i >= 30000 and i <= 39999:
                regContent = self.modbusClientObj.read_input_registers(i)
            else:
                # will probably error as the pyModbusTCp library checks addresses
                regContent = self.modbusClientObj.read_holding_registers(i)


            #self.debugLog("regContent returned " + str(regContent))

            if str(regContent) != "[0]":
                self.registerCount = self.registerCount + 1

            #self.registerArray.append(str(regContent))
            self.registerArray.append((i, str(regContent)))

            if dpg != None:
                dpg.configure_item( progressBar, default_value=(i-min)/(max-min-1) )

    


    def checkChangedRegisters(self, min, max, dpg = None, progressBar = None, statusText=None):
        self.debugLog("searchChangedRegisters")

        if self.connected == False:
            self.debugLog("search changed called but not connected")
            return False

        if len(self.registerArray) == 0:
            self.debugLog("searchChanged called but haven't yet scanned registers to start with")
            dpg.configure_item( statusText, default_value="Scan Registers First") 
            return False

        max = int(max)
        min = int(min)

        # min > 0 && < max
        # max < 65535
        if max > 65535:
            self.debugLog("Register addresses only go up to 65536")
            return False

        if min < 0 or min > max:
            self.debugLog("Invalid minimum register address")
            return False
        self.changedRegisterArray = False
        self.changedRegisterArray = list()        
        
        for i in range(min,max):
            if i >= 40000 and i <= 49999:
                regContent = self.modbusClientObj.read_holding_registers(i)
            elif i >= 30000 and i <= 39999:
                regContent = self.modbusClientObj.read_input_registers(i)
            else:
                # will probably error as the pyModbusTCp library checks addresses
                regContent = self.modbusClientObj.read_holding_registers(i)


            #self.debugLog("regContent returned " + str(regContent))
            for register in self.registerArray:
                if register[0] == i:
                    if str(register[1]) != str(regContent):
                        self.changedRegisterArray.append((str(i),str(regContent)))
            #self.registerArray.append(str(regContent))

            if dpg != None:
                dpg.configure_item( progressBar, default_value=(i-min)/(max-min-1) )

        if len(self.changedRegisterArray) > 0:
            dpg.configure_item( statusText, default_value=str(len(self.changedRegisterArray)) + " registers changed") 
        else:
            dpg.configure_item( statusText, default_value="No registers changed") 


    def scanCoils(self, min, max, dpg = None, progressBar = None):
        self.debugLog("ScanCoils")
        if self.connected == False:
            self.debugLog("scan called but not connected")
            return False

        
        self.coilCount = 0

        max = int(max)
        min = int(min)

        # min > 0 && < max
        # max < 65536
        if max > 65536:
            self.debugLog("Coil addresses only go up to 65536")
            return False

        if min < 0 or min > max:
            self.debugLog("Invalid minimum coil address")
            return False


        for i in range(min,max):
            regContent = None
            #pyModbusTCP supports coil reading 0-65535 regardless of type
            regContent = self.modbusClientObj.read_coils(i)

            #self.debugLog("regContent returned " + str(regContent))

            if str(regContent) == "[True]":
                #self.debugLog("Found coil set at " + str(i))
                self.coilCount = self.coilCount + 1  
            #else:
                #self.debugLog("Error retreiving coil " + str(i))

            if dpg != None:
                dpg.configure_item(progressBar, default_value=(i-min)/(max-min-1))
                
            #self.debugLog("Adding " + str(regContent) + " to array position " + str(i))
            self.coilArray.append(regContent)

        self.debugLog("Found " + str(self.coilCount) + " configured coils")



    # returns a single coil value
    def getCoil(self, address):
        self.debugLog("getCoil: " + str(address))
        if self.connected == False:
            self.debugLog("getCoil called but not connected")
            return False

        address = int(address)

        coilValue = self.modbusClientObj.read_coils(address)
        self.debugLog("value: " + str(coilValue))
        if str(coilValue) == "[True]":
            #self.debugLog("returning true")
            return True
        else:
            return False


    def setCoil(self, address, value):
        self.debugLog("setCoil: " + str(address))
        if self.connected == False:
            self.debugLog("setCoil called but not connected")
            return False

        #set_coils(self, address, bit_list, _srv_infos=None):

        return self.modbusClientObj.write_single_coil(int(address), int(value))


  # returns a single coil value
    def getRegister(self, address):
        self.debugLog("getRegister: " + str(address))
        if self.connected == False:
            self.debugLog("getRegister called but not connected")
            return False

        address = int(address)

        if address >= 40000 and address <= 49999:
                regContent = self.modbusClientObj.read_holding_registers(address)
        elif address >= 30000 and address <= 39999:
            regContent = self.modbusClientObj.read_input_registers(address)
        else:
            # will probably error as the pyModbusTCp library checks addresses
            regContent = self.modbusClientObj.read_holding_registers(address)

        self.debugLog("value: " + str(regContent))
        return regContent




    def setRegister(self, address, value):
        self.debugLog("setRegister: " + str(address))
        if self.connected == False:
            self.debugLog("setRegister called but not connected")
            return False

        #set_coils(self, address, bit_list, _srv_infos=None):

        return self.modbusClientObj.write_single_register(int(address), int(value))



    def showConfiguredRegisters(self, min=0, hidezero=False):
        if self.registerArray == None:
            self.debugLog("Empty register array")
            return False

        self.debugLog("showConfiguredRegisters on array size " + str(len(self.registerArray)))
        output = ""
        for i in range(0,len(self.registerArray)):
            if hidezero == True:
                
                if str(self.registerArray[i][1]) != "[0]":
                    output = output + str(self.registerArray[i][0] ) + ":" + str(self.registerArray[i][1]) + "\n"
            else:
                output = output + str(self.registerArray[i][0] ) + ":" + str(self.registerArray[i][1]) + "\n"
            
        return output



    def showChangedRegisters(self, min=0):
        self.debugLog("showChangedRegisters on array size " + str(len(self.changedRegisterArray)))
        if self.registerArray == None: # have not scanned at all yet
            self.debugLog("Empty register array")
            return False
        
        if self.changedRegisterArray == None: # have not scanned for changes
            return self.showConfiguredRegisters(min)
        
        if len(self.changedRegisterArray) == 0: # have scanned for changes but nothing found
            return self.showConfiguredRegisters(min)
             
        output = ""
        for i in range(0,len(self.registerArray)):
            thisChanged = False

        
            for register in self.changedRegisterArray:
                #self.debugLog("comparing reg0: " + str(register[0]) + " to i: " + str(self.registerArray[i][0]) )
                if str(register[0]) == str(self.registerArray[i][0]):# it has changed                    
                    output = output + str(self.registerArray[i][0] ) + ":" + str(self.registerArray[i][1]) + " => "+ str(register[1]) +"\n"
                    thisChanged = True

            if thisChanged == False:
                    output = output + str(self.registerArray[i][0] ) + ":" + str(self.registerArray[i][1]) + "\n"
        
        return output




    def showOnlyChangedRegisters(self):
        self.debugLog("showOnlyChangedRegisters on array size " + str(len(self.changedRegisterArray)))
        if self.registerArray == None: # have not scanned at all yet
            self.debugLog("Empty register array")
            return False
        
        if self.changedRegisterArray == None: # have not scanned for changes
            self.debugLog("Empty changed register array")
            return False
        
        if len(self.changedRegisterArray) == 0: # have scanned for changes but nothing found
            self.debugLog("Empty changed register array")
            return False
             
        output = ""
        for i in range(0,len(self.changedRegisterArray)):
        
            for register in self.registerArray:
                #self.debugLog("comparing reg0: " + str(register[0]) + " to i: " + str(self.registerArray[i][0]) )
                if str(register[0]) == str(self.changedRegisterArray[i][0]):# it has changed                   
                    output = output + str(self.changedRegisterArray[i][0] ) + ":" + str(register[1]) + " => " + str(self.changedRegisterArray[i][1])  +"\n"
        
        return output


    def showConfiguredCoils(self):        
        if self.coilArray == None:
            self.debugLog("Empty coil array")
            return False
        
        self.debugLog("showConfiguredCoils on array size " + str(len(self.coilArray)))
        output = ""

        #max line length before inserting a linefeed
        linelen = 150
        for i in range(0,len(self.coilArray)):
            #self.debugLog("array entry = " + str(self.coilArray[i]))
            if str(self.coilArray[i]) == "[True]":

                if len(output)>0 and i<(len(self.coilArray)):
                    output = output + ", "

                if len(output) > linelen:
                    if len(output) % linelen > (linelen-6):
                        output = output + "\n"
             

                output = output + str(i)
                #self.debugLog("adding " + str(i))

        return output


    def debugLog(self,data = None):
        print(data)
        




#
# Code to draw the GUI
#

import dearpygui.dearpygui as dpg



dpg.create_context()
modbusServer = modbusServer()

#print any debug info text into console
def debugLog(text):
    print(text)


def testConnection(sender, app_data, user_data):
    modbusServer.setAddress(dpg.get_value("serverAddress"))
    modbusServer.setPort(dpg.get_value("serverPort"))

    if modbusServer.connect() == True:
        dpg.configure_item("connectionStatus", default_value="Connected")
        dpg.bind_item_theme("connectionStatus", green_bg_theme)
    else:
        dpg.configure_item("connectionStatus", default_value="Connection Failed")
        dpg.bind_item_theme("connectionStatus", red_bg_theme)




def scanModbusCoils(sender, app_data):
    debugLog("scanModbusValues")
    testConnection("uNF","uNF","uNF")
    dpg.configure_item("configuredCoils", default_value="Scanning...")
    modbusServer.scanCoils(dpg.get_value("minCoil"), dpg.get_value("maxCoil"), dpg,"coilProgress")
    dpg.configure_item("configuredCoils", default_value=modbusServer.showConfiguredCoils())



def scanModbusRegisters(sender, app_data):
    debugLog("scanRegisters")
    testConnection("uNF","uNF","uNF")
    dpg.configure_item("configuredRegisters", default_value="Scanning...")
    modbusServer.scanRegisters(dpg.get_value("minReg"), dpg.get_value("maxReg"), dpg,"registerProgress")
    dpg.configure_item("configuredRegisters", default_value=modbusServer.showConfiguredRegisters( dpg.get_value("minReg") , False) )

def setCoilGetValue(sender, app_data):
    debugLog("setCoilGetValue")
    testConnection("uNF","uNF","uNF")
    if (modbusServer.getCoil(dpg.get_value("setCoilAddress"))):
        #true
        dpg.configure_item("setCoilValue", default_value="1") 
        dpg.bind_item_theme("setCoilValue", green_bg_theme)
    else:
        #false
        dpg.configure_item("setCoilValue", default_value="0") 
        dpg.bind_item_theme("setCoilValue", red_bg_theme)


def setCoilValue(sender, app_data):
    debugLog("setCoilValue")
    testConnection("uNF","uNF","uNF")
    if (modbusServer.setCoil(dpg.get_value("setCoilAddress"), dpg.get_value("setCoilAddressNewValueInput"))):
        #true
        dpg.configure_item("setCoilAddressNewValueStatus", default_value="Success") 
        dpg.bind_item_theme("setCoilAddressNewValueStatus", green_bg_theme)
        setCoilGetValue("uNF", "uNF")
    else:
        #false
        dpg.configure_item("setCoilAddressNewValueStatus", default_value="Failed") 
        dpg.bind_item_theme("setCoilAddressNewValueStatus", red_bg_theme)

def helpRegisters(sender, app_data):
    dpg.configure_item("configuredRegisters", default_value="Ranges are usually:\n30001-39999 for analogue input registers\n40001-49999 for analogue output holding registers (Read/Write)\n")


def setRegisterGetValue(sender, app_data):
    debugLog("setRegisterGetValue")
    testConnection("uNF","uNF","uNF")
    result = modbusServer.getRegister(dpg.get_value("setRegisterAddress"))
    if (result):
        #true
        dpg.configure_item("setRegisterGetValue", default_value=str(result)) 
        dpg.bind_item_theme("setRegisterGetValue", green_bg_theme)
        
    else:
        #false
        dpg.configure_item("setRegisterGetValue", default_value="Failed Read") 
        dpg.bind_item_theme("setRegisterGetValue", red_bg_theme)



def setRegisterValue(sender, app_data):
    debugLog("setRegisterValue")
    testConnection("uNF","uNF","uNF")
    result = modbusServer.setRegister(dpg.get_value("setRegisterAddress"), dpg.get_value("setRegisterAddressNewValueInput"))
    if (result):
        #true
        dpg.configure_item("setRegisterAddressNewValueStatus", default_value="Success") 
        dpg.bind_item_theme("setRegisterAddressNewValueStatus", green_bg_theme)
        setRegisterGetValue("uNF", "uNF")
    else:
        #false
        dpg.configure_item("setRegisterAddressNewValueStatus", default_value="Failed") 
        dpg.bind_item_theme("setRegisterAddressNewValueStatus", red_bg_theme)


def hideZeroRegisters(sender, app_data):
    debugLog(f"outputRegisterTextChanged - sender: {sender}, \t app_data: {app_data}")
    testConnection("uNF","uNF","uNF")

    if (app_data == True): #the box was ticked
        #hide the zero entries
        dpg.configure_item("configuredRegisters", default_value=modbusServer.showConfiguredRegisters( dpg.get_value("minReg") , True ) )   
    else:
        #show all entries
        dpg.configure_item("configuredRegisters", default_value=modbusServer.showConfiguredRegisters( dpg.get_value("minReg") , False ) )   



def findChangingRegisters(sender, app_data):
    debugLog("findChangingRegisters")
    testConnection("uNF","uNF","uNF")
    dpg.configure_item("findChangingRegisterStatus", default_value="Scanning...")
    modbusServer.checkChangedRegisters(dpg.get_value("minReg"), dpg.get_value("maxReg"), dpg,"registerProgress", "findChangingRegisterStatus" )
    dpg.configure_item("configuredRegisters", default_value=modbusServer.showChangedRegisters( dpg.get_value("minReg") ) )

def showOnlyChangedRegisters(sender, app_data):
    debugLog("showOnlyChangedRegisters")
    
    if (app_data == True): #the box was ticked
        #hide the zero entries
        dpg.configure_item("configuredRegisters", default_value=modbusServer.showOnlyChangedRegisters( ) )
    else:
        #show all entries
        dpg.configure_item("configuredRegisters", default_value=modbusServer.showChangedRegisters( dpg.get_value("minReg") ) )



with dpg.theme() as green_bg_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 153, 0), category=dpg.mvThemeCat_Core)
        

with dpg.theme() as red_bg_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (230, 0, 0), category=dpg.mvThemeCat_Core)

       
with dpg.theme() as grey_txt_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (150, 150, 150))

with dpg.theme() as white_txt_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))

# Uses open Sans font from https://github.com/adobe-fonts/source-sans
# License for this font: https://github.com/adobe-fonts/source-sans/blob/release/LICENSE.md
with dpg.font_registry():
    default_font = dpg.add_font("SourceSans3-Regular.otf", 20)


with dpg.window(tag="Primary Window"):
    dpg.bind_font(default_font)
    dpg.add_text("Modbus/TCP Server Address:", tag="serverText")
    dpg.add_input_text( default_value="127.0.0.1",  tag="serverAddress", width=250, indent=200)
    serverAddressGroup = dpg.add_group(horizontal=True)
    dpg.move_item("serverText", parent=serverAddressGroup)
    dpg.move_item("serverAddress", parent=serverAddressGroup)
    

    dpg.add_text("Port:", tag="serverPortText")
    dpg.add_input_text(default_value="10502", tag="serverPort", width=100, indent=200)
    
    serverPortGroup = dpg.add_group(horizontal=True)
    dpg.move_item("serverPortText", parent=serverPortGroup)
    dpg.move_item("serverPort", parent=serverPortGroup)


    dpg.add_button(label="Test Connection", callback=testConnection, tag="testButton")
    dpg.add_text("Connection Status:", tag="connectionstatusText")
    dpg.add_input_text(default_value="Not Connected", tag="connectionStatus" , width=150, readonly=True, indent=200)
    serverStatusGroup = dpg.add_group(horizontal=True)
    dpg.move_item("connectionstatusText", parent=serverStatusGroup)
    dpg.move_item("connectionStatus", parent=serverStatusGroup)
    dpg.move_item("testButton", parent=serverStatusGroup)

    #scan coils
    dpg.add_tab_bar()
    dpg.add_button(label="Scan Coils", tag="scanCoilButton", callback=scanModbusCoils)
    dpg.add_input_text( default_value="0",  tag="minCoil", label="min (0)", width=50, indent=200)
    dpg.add_input_text( default_value="1000",  tag="maxCoil", label="max (65535)", width=50, indent=350)
    coilGroup = dpg.add_group(horizontal=True)
    dpg.move_item("scanCoilButton", parent=coilGroup)
    dpg.move_item("minCoil", parent=coilGroup)
    dpg.move_item("maxCoil", parent=coilGroup)
    dpg.add_progress_bar(label="Coil Scan Progress", tag="coilProgress")
    dpg.add_input_text(default_value="Not Yet Scanned - Set min & max address values (below 65536) and click 'scan coils'.\nNote scanning thousands of coils will take a LONG time, recommended to do a few hundred to test at first!\n\nTypical Ranges:\n1-9999 discrete output coils\n10001 - 19999 - discrete input contacts ", tag="configuredCoils" , readonly=True, multiline=True)
    


    # scan registers
    dpg.add_tab_bar()
    dpg.add_button(label="Scan Registers", tag="scanRegisterButton", callback=scanModbusRegisters)
    dpg.add_input_text( default_value="30000",  tag="minReg", label="min (0)", width=50, indent=200)
    dpg.add_input_text( default_value="49999",  tag="maxReg", label="max (65535)", width=50, indent=350)
    dpg.add_checkbox(tag="hideZero", callback=hideZeroRegisters, label="hide 0", indent=550) 
    dpg.add_button(label="Help", tag="helpRegisterButton", callback=helpRegisters, indent=700)
    registerGroup = dpg.add_group(horizontal=True)
    dpg.move_item("scanRegisterButton", parent=registerGroup)
    dpg.move_item("minReg", parent=registerGroup)
    dpg.move_item("maxReg", parent=registerGroup)
    dpg.move_item("hideZero", parent=registerGroup)
    dpg.move_item("helpRegisterButton", parent=registerGroup)
    dpg.add_progress_bar(label="Register Scan Progress", tag="registerProgress")
    dpg.add_input_text(default_value="Not Yet Scanned...\nRanges are usually:\n30000-39999 for analogue input registers\n40000-49999 for analogue output holding registers (Read/Write)\n", tag="configuredRegisters" , readonly=True, multiline=True)
    
    dpg.add_button(label="Search for Changes", tag="findChangingRegistersButton", callback=findChangingRegisters)
    dpg.add_input_text(default_value="Not Scanned", tag="findChangingRegisterStatus" , width=250, readonly=True, indent=200)
    dpg.add_checkbox(tag="onlyChangesCheckbox", callback=showOnlyChangedRegisters, label="Show Only Changes", indent=550) 
    registerGroup2 = dpg.add_group(horizontal=True)
    dpg.move_item("findChangingRegistersButton", parent=registerGroup2)
    dpg.move_item("findChangingRegisterStatus", parent=registerGroup2)
    dpg.move_item("onlyChangesCheckbox", parent=registerGroup2)

# 1-9999 - discrete output coils R/W - binary
# 10001 - 19999 - discrete input contacts R/O - binary

    
    # set coil values
    dpg.add_tab_bar()
    with dpg.collapsing_header(label="Configure Coils / Contacts "):
        dpg.add_text("Use this to set binary values on a Modbus Server, typically addresses 1-9999 may be writable.", tag="setCoilText")
        dpg.add_text("Address to Configure:", tag="setCoilAddressText")
        dpg.add_input_text( default_value="1",  tag="setCoilAddress", indent=200, width=50)
        dpg.add_button(label="Get Current", tag="setCoilGetValueButton", callback=setCoilGetValue, width=100, indent=400)
        dpg.add_input_text( default_value="Not Scanned",  tag="setCoilValue", width=100, indent=700, readonly=True)
        setCoilGroup1 = dpg.add_group(horizontal=True)
        dpg.move_item("setCoilAddressText", parent=setCoilGroup1)
        dpg.move_item("setCoilAddress", parent=setCoilGroup1)
        dpg.move_item("setCoilGetValueButton", parent=setCoilGroup1)
        dpg.move_item("setCoilValue", parent=setCoilGroup1)

        dpg.add_text("Set Value (0 or 1)", tag="setCoilAddressNewValueText")
        dpg.add_input_text( default_value="1",  tag="setCoilAddressNewValueInput", indent=200, width=50)
        dpg.add_button(label="Set", tag="setCoilAddressNewValueButton", callback=setCoilValue, width=50, indent=400)
        dpg.add_input_text( default_value="Not Attempted",  tag="setCoilAddressNewValueStatus", width=100, indent=700, readonly=True)
        setCoilGroup2 = dpg.add_group(horizontal=True)
        dpg.move_item("setCoilAddressNewValueText", parent=setCoilGroup2)
        dpg.move_item("setCoilAddressNewValueInput", parent=setCoilGroup2)
        dpg.move_item("setCoilAddressNewValueButton", parent=setCoilGroup2)
        dpg.move_item("setCoilAddressNewValueStatus", parent=setCoilGroup2)



# 30001 - 39999 - analog input registers - R/O - 16 bit int
# 40001 - 49999 - analog output holding registers - R/W - 16 bit int

    # set register values
    dpg.add_tab_bar()
    with dpg.collapsing_header(label="Configure Registers"):
        dpg.add_text("Use this to set register values on a Modbus Server, typically addresses 40001-49999 would be writable", tag="setRegisterText")
        dpg.add_text("Address to Configure:", tag="setRegisterAddressText")
        dpg.add_input_text( default_value="40001",  tag="setRegisterAddress", indent=200, width=50)
        dpg.add_button(label="Get Current", tag="setRegisterGetValueButton", callback=setRegisterGetValue, width=100, indent=400)
        dpg.add_input_text( default_value="Not Scanned",  tag="setRegisterGetValue", width=100, indent=700, readonly=True)
        setRegisterGroup1 = dpg.add_group(horizontal=True)
        dpg.move_item("setRegisterAddressText", parent=setRegisterGroup1)
        dpg.move_item("setRegisterAddress", parent=setRegisterGroup1)
        dpg.move_item("setRegisterGetValueButton", parent=setRegisterGroup1)
        dpg.move_item("setRegisterGetValue", parent=setRegisterGroup1)

        dpg.add_text("Set Value (0-65535)", tag="setRegisterAddressNewValueText")
        dpg.add_input_text( default_value="10",  tag="setRegisterAddressNewValueInput", indent=200, width=50)
        dpg.add_button(label="Set", tag="setRegisterAddressNewValueButton", callback=setRegisterValue, width=50, indent=400)
        dpg.add_input_text( default_value="Not Attempted",  tag="setRegisterAddressNewValueStatus", width=100, indent=700, readonly=True)
        setRegisterGroup2 = dpg.add_group(horizontal=True)
        dpg.move_item("setRegisterAddressNewValueText", parent=setRegisterGroup2)
        dpg.move_item("setRegisterAddressNewValueInput", parent=setRegisterGroup2)
        dpg.move_item("setRegisterAddressNewValueButton", parent=setRegisterGroup2)
        dpg.move_item("setRegisterAddressNewValueStatus", parent=setRegisterGroup2)

dpg.create_viewport(title='pyModbusScanner')
 
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()

        


