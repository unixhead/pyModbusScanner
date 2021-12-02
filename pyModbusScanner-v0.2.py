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
    port = 502
    debugLogData="modbusServer Debug Log\n"

    def __init__(self):
        self.modbusClientObj = ModbusClient() # reference to the pyModbusTCP object used
        

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
            self.debugLog("Coil addresses only go up to 65536")
            return False

        if min < 0 or min > max:
            self.debugLog("Invalid minimum coil address")
            return False

        self.registerArray = list()
        self.registerCount = 0

        
        
        for i in range(min,max):
            regContent = self.modbusClientObj.read_holding_registers(i)
            self.debugLog("regContent returned " + str(regContent))

            if str(regContent) != "[0]":
                self.registerCount = self.registerCount + 1

            self.registerArray.append(str(regContent))

            if dpg != None:
                dpg.configure_item(progressBar, default_value=i/(max-1))

            

    def scanInputRegisters(self, min, max, dpg = None, progressBar = None):
        self.debugLog("ScanInputRegisters")

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
            self.debugLog("Invalid minimum Register address")
            return False

        self.inputRegisterArray = list()
        self.inputRegisterCount = 0
        
        for i in range(min,max):
            regContent = self.modbusClientObj.read_input_registers(i)
            self.debugLog("regContent returned " + str(regContent))

            if str(regContent) != "[0]":
                self.inputRegisterCount = self.inputRegisterCount + 1

            self.inputRegisterArray.append(str(regContent))

            if dpg != None:
                dpg.configure_item(progressBar, default_value=i/(max-1))




    def scanCoils(self, min, max, dpg = None, progressBar = None):
        self.debugLog("ScanCoils")
        if self.connected == False:
            self.debugLog("scan called but not connected")
            return False

        self.coilArray = list()
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
            regContent = self.modbusClientObj.read_coils(i)
            self.debugLog("regContent returned " + str(regContent))

            if str(regContent) == "[True]":
                self.debugLog("Found coil set at " + str(i))
                self.coilCount = self.coilCount + 1  
            else:
                self.debugLog("Error retreiving coil " + str(i))

            if dpg != None:
                dpg.configure_item(progressBar, default_value=i/(max-1))
                
            #self.debugLog("Adding " + str(regContent) + " to array position " + str(i))
            self.coilArray.append(regContent)

        self.debugLog("Found " + str(self.coilCount) + " configured coils")


    def showConfiguredRegisters(self):
        if self.registerArray == None:
            self.debugLog("Empty register array")
            return False

        self.debugLog("showConfiguredRegisters on array size " + str(len(self.registerArray)))
        output = ""
        for i in range(0,len(self.registerArray)):
            output = output + str(i) + ":" + str(self.registerArray[i]) + "\n"
            
        return output


    def showConfiguredInputRegisters(self):
        if self.inputRegisterArray == None:
            self.debugLog("Empty input register array")
            return False

        self.debugLog("showConfiguredInputRegisters on array size " + str(len(self.inputRegisterArray)))
        output = ""
        for i in range(0,len(self.inputRegisterArray)):
            output = output + str(i) + ":" + str(self.inputRegisterArray[i]) + "\n"
            
        return output


    def showConfiguredCoils(self):        
        if self.coilArray == None:
            self.debugLog("Empty coil array")
            return False
        
        self.debugLog("showConfiguredCoils on array size " + str(len(self.coilArray)))
        output = ""
        for i in range(0,len(self.coilArray)):
            #self.debugLog("array entry = " + str(self.coilArray[i]))
            if str(self.coilArray[i]) == "[True]":
                if len(output)>0 and i<(len(self.coilArray)-1):
                    output = output + ", "

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
        dpg.bind_item_theme("scanCoilButton", white_txt_theme)
        dpg.bind_item_theme("scanRegisterButton", white_txt_theme)
        dpg.bind_item_theme("scanInputButton", white_txt_theme)
        dpg.configure_item("configuredCoils", default_value="Not Yet Scanned - Set min & max address values (below 65536) and click 'scan coils'.\nNote scanning thousands of coils will take a LONG time, recommended to do a few hundred to test at first!")
        dpg.configure_item("configuredRegisters", default_value="Not Yet Scanned...")
        dpg.configure_item("configuredInputRegisters", default_value="Not Yet Scanned...")
    else:
        dpg.configure_item("connectionStatus", default_value="Connection Failed")
        dpg.bind_item_theme("connectionStatus", red_bg_theme)
        dpg.bind_item_theme("scanCoilButton", grey_txt_theme)
        dpg.bind_item_theme("scanRegisterButton", grey_txt_theme)
        dpg.bind_item_theme("scanInputButton", grey_txt_theme)
        dpg.configure_item("configuredCoils", default_value="Test connection before scanning")
        dpg.configure_item("configuredRegisters", default_value="Test connection before scanning")
        dpg.configure_item("configuredInputRegisters", default_value="Test connection before scanning")

    debugLog(modbusServer.debugLog())


def scanModbusCoils(sender, app_data):
    debugLog("scanModbusValues")
    dpg.configure_item("configuredCoils", default_value="Scanning...")
    modbusServer.scanCoils(dpg.get_value("minCoil"), dpg.get_value("maxCoil"), dpg,"coilProgress")
    dpg.configure_item("configuredCoils", default_value=modbusServer.showConfiguredCoils())



def scanModbusRegisters(sender, app_data):
    debugLog("scanRegisters")
    dpg.configure_item("configuredRegisters", default_value="Scanning...")
    modbusServer.scanRegisters(dpg.get_value("minReg"), dpg.get_value("maxReg"), dpg,"registerProgress")
    dpg.configure_item("configuredRegisters", default_value=modbusServer.showConfiguredRegisters())



def scanInputRegisters(sender, app_data):
    debugLog("scanInputRegisters")
    dpg.configure_item("configuredInputRegisters", default_value="Scanning...")
    modbusServer.scanInputRegisters(dpg.get_value("minInp"), dpg.get_value("maxInp"), dpg,"InputRegisterProgress")
    dpg.configure_item("configuredInputRegisters", default_value=modbusServer.showConfiguredInputRegisters())



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
    dpg.add_input_text(default_value="502", tag="serverPort", width=100, indent=200)
    
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
    dpg.add_input_text( default_value="0",  tag="minCoil", label="min", width=50, indent=200)
    dpg.add_input_text( default_value="65535",  tag="maxCoil", label="max", width=50, indent=300)
    dpg.bind_item_theme("scanCoilButton", grey_txt_theme)
    coilGroup = dpg.add_group(horizontal=True)
    dpg.move_item("scanCoilButton", parent=coilGroup)
    dpg.move_item("minCoil", parent=coilGroup)
    dpg.move_item("maxCoil", parent=coilGroup)
    dpg.add_progress_bar(label="Coil Scan Progress", tag="coilProgress")
    dpg.add_input_text(default_value="Test connection before scanning", tag="configuredCoils" , readonly=True, multiline=True)
    
    # scan registers
    dpg.add_tab_bar()
    dpg.add_button(label="Scan Registers", tag="scanRegisterButton", callback=scanModbusRegisters)
    dpg.add_input_text( default_value="0",  tag="minReg", label="min", width=50, indent=200)
    dpg.add_input_text( default_value="65535",  tag="maxReg", label="max", width=50, indent=300)
    dpg.bind_item_theme("scanRegisterButton", grey_txt_theme)
    registerGroup = dpg.add_group(horizontal=True)
    dpg.move_item("scanRegisterButton", parent=registerGroup)
    dpg.move_item("minReg", parent=registerGroup)
    dpg.move_item("maxReg", parent=registerGroup)
    dpg.add_progress_bar(label="Register Scan Progress", tag="registerProgress")
    dpg.add_input_text(default_value="Test connection before scanning", tag="configuredRegisters" , readonly=True, multiline=True)
    


    # scan input registers
    dpg.add_tab_bar()
    dpg.add_button(label="Scan Input Registers", tag="scanInputButton", callback=scanInputRegisters)
    dpg.add_input_text( default_value="0",  tag="minInp", label="min", width=50, indent=200)
    dpg.add_input_text( default_value="65535",  tag="maxInp", label="max", width=50, indent=300)
    dpg.bind_item_theme("scanInputButton", grey_txt_theme)
    inputRegisterGroup = dpg.add_group(horizontal=True)
    dpg.move_item("scanInputButton", parent=inputRegisterGroup)
    dpg.move_item("minInp", parent=inputRegisterGroup)
    dpg.move_item("maxInp", parent=inputRegisterGroup)
    dpg.add_progress_bar(label="Input Register Scan Progress", tag="InputRegisterProgress")
    dpg.add_input_text(default_value="Test connection before scanning", tag="configuredInputRegisters" , readonly=True, multiline=True)



dpg.create_viewport(title='pyModbusScanner')
 
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()

        


