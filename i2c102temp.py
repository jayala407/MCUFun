# MicroPython driver for Sparkfun TMP102 board 
# by Joe Ayala
# GPL License
# a blatent copy of the Arduino Driver on the Sparkfun GitHub
# https://github.com/sparkfun/SparkFun_TMP102_Arduino_Library
#

from machine import Pin, I2C
# constants
global T102ADDR,registerByte,replaceByte,commandByte,CONFIG_REGISTER,T_LOW_REGISTER,T_HIGH_REGISTER  

C_TEMPERATURE_REGISTER = b'\x00'
C_CONFIG_REGISTER = b'\x01'
C_T_LOW_REGISTER = b'\x02'
C_T_HIGH_REGISTER   = b'\x03'
 
T102ADDR = 0x48



commandByte = bytearray(1)
registerByte = bytearray(2)
replaceByte = bytearray(3)



TEMPERATURE_REGISTER = 0x00  
CONFIG_REGISTER  = 0x01
T_LOW_REGISTER  = 0x02 
T_HIGH_REGISTER = 0x03
 

class T102 :
    def __init__(self):
        self.addr = T102ADDR
        self.i2c = I2C(0)  #use pico defaults
        self.alertPin = None
        
    def init(self, AlertPin = None):    
        if (self.i2c.scan()[0] != T102ADDR ):
            print("Init Error, device not found")
            return(1)
        else:
            if (AlertPin != None):
                self.alertPin = Pin(AlertPin)
                print("alertPin  : "+str(AlertPin))
            print("I2C Address      : "+str(hex(self.i2c.scan()[0]))) # Display device address
            print("I2C Configuration: "+str(self.i2c) )                  # Display I2C config
            return (0)
    
    def openPointerRegister(self,pointerReg):
        #print("Opening register = ",pointerReg)
        self.i2c.writeto(self.addr,pointerReg,True)           # Open specified register
         
    
    def readRegister(self):
    
        # Read 2 bytes of whatever is the current configuration register value
        # dummyByte = self.i2c.readfrom(self.addr ,2,False)
        # print ("readRegister = ",dummyByte)
        # return dummyByte
        return  self.i2c.readfrom(self.addr,2,False)
        

    def readTempC(self) :

         # // Read Temperature
         # // Change pointer address to temperature register (0)
         self.openPointerRegister(C_TEMPERATURE_REGISTER)
         #  Read from temperature register
         registerByte  = self.readRegister()

         if ((registerByte[0] == 0xFF) & (registerByte[1] == 0xFF)):
              return NAN
         if (registerByte[1] & 0x01):  #13 bit mode
             #combine bytes to create a signed int
            digitalTemp = ((registerByte[0]) << 5) | (registerByte[1] >> 3)
            # Temperature data can be + or -, if it should be negative,
            # convert 13 bit to 16 bit and use the 2s compliment.
            if (digitalTemp > 0xFFF):
                digitalTemp |= 0xE000
         else: #12 bit mode
            digitalTemp = ((registerByte[0]) << 4) | (registerByte[1] >> 4)
            # Temperature data can be + or -, if it should be negative,
            # convert 13 bit to 16 bit and use the 2s compliment.
            if (digitalTemp > 0x7FF):
                digitalTemp |= 0xF000
         return digitalTemp * 0.0625  #Convert digital reading to analog temperature (1-bit is equal to 0.0625 C)

    def readTempF(self):
        return self.readTempC() * 9.0 / 5.0 + 32.0

    def setConversionRate(self,rate):
        rate = rate & 0x03  #Make sure rate is not set higher than 3.
        # print("Conversion Rate setting = ", rate)
        # Change pointer address to configuration register (0x01)
        self.openPointerRegister(C_CONFIG_REGISTER)
        # Read current configuration register value
        registerByte = self.readRegister()
        # Load new conversion rate
        replaceByte1 = registerByte[1] & 0x3F      # Clear CR0/1 (bit 6 and 7 of second byte)
        replaceByte1 |= rate << 6 # Shift in new conversion rate
        #  Set configuration registers
        replaceByte[0] = CONFIG_REGISTER
        replaceByte[1] = registerByte[0] 
        replaceByte[2] = replaceByte1
        #print("writing conversion rate ", replaceByte)
        self.i2c.writeto(self.addr,replaceByte,True) # Point to configuration register        self.i2c.writeto(self.addr,t102Registers['CONFIG_REGISTER']) # Point to configuration register

    def setExtendedMode(self, mode):
        #print("extendedMode = ", mode)
        self.openPointerRegister(C_CONFIG_REGISTER)

        # Read current configuration register value
        registerByte = self.readRegister()
        #Load new value for extention mode
        replaceByte1 = registerByte[1] & 0xEF  #  Clear EM (bit 4 of second byte)
        replaceByte1 |= mode << 4  # Shift in new exentended mode bit
        # Set configuration registers
        replaceByte[0] = CONFIG_REGISTER
        replaceByte[1] = registerByte[0]  
        replaceByte[2] = replaceByte1
        #print("writing Extended mode ", replaceByte)
        self.i2c.writeto(self.addr,replaceByte,True)
     
    def sleep(self):
        # print("Sleep...")
        self.openPointerRegister(C_CONFIG_REGISTER)
        # Read current configuration register value
        registerByte = self.readRegister()
        replaceByte0 = registerByte[0] | 0x01; # Set SD (bit 0 of first byte)
        # Set configuration register
        replaceByte[0] = CONFIG_REGISTER
        replaceByte[1] = replaceByte0 
        replaceByte[2] = registerByte[1]
        self.i2c.writeto(self.addr,replaceByte,True) # Point to configuration register        self.i2c.writeto(self.addr,t102Registers['CONFIG_REGISTER']) # Point to configuration register

    def wakeup(self):
        #print("Wake...")
        self.openPointerRegister(C_CONFIG_REGISTER)
        # Read current configuration register value
        registerByte = self.readRegister()
        replaceByte0 = registerByte[0] & 0xFE  #  Clear SD (bit 0 of first byte)
        # Set configuration register
        replaceByte[0] = CONFIG_REGISTER
        replaceByte[1] = replaceByte0 
        replaceByte[2] = registerByte[1]
        self.i2c.writeto(self.addr,replaceByte,True) # Point to configuration register        self.i2c.writeto(self.addr,t102Registers['CONFIG_REGISTER']) # Point to configuration register

    def setAlertPolarity(self, polarity):
        #print("alertPolarity = ",polarity)
        self.openPointerRegister(C_CONFIG_REGISTER)
        # Read current configuration register value
        registerByte = self.readRegister()
        # Load new value for polarity
        replaceByte0  = registerByte[0] & 0xFB           #  Clear POL (bit 2 of registerByte)
        replaceByte0  |= polarity << 2  #  Shift in new POL bit
        # Set configuration register
        replaceByte[0] = CONFIG_REGISTER
        replaceByte[1] = replaceByte0 # CONFIG_REGISTER still open
        replaceByte[2] = registerByte[1]
        #print("writing polarity..",replaceByte)
        self.i2c.writeto(self.addr,replaceByte,True) # Point to configuration register        self.i2c.writeto(self.addr,t102Registers['CONFIG_REGISTER']) # Point to configuration register
   
    def alert(self):
        if (self.alertPin != None):
            self.openPointerRegister(C_CONFIG_REGISTER)
            # Read current configuration register value
            registerByte = self.readRegister()
            # Clear everything but the alert bit (bit 5)
            return (registerByte[1] & 0x20) >> 5
        else:
            return 0

    def oneShot(self, setOneShot):
        self.openPointerRegister(C_CONFIG_REGISTER)
        registerByte = self.readRegister()

        if (setOneShot) : # Enable one-shot by writing a 1 to the OS bit of the configuration register
  
            replaceByte0 = registerByte[0]| (1 << 7)

            # Set configuration register
            replaceByte[0] = CONFIG_REGISTER
            replaceByte[1] = replaceByte0
            replaceByte[2] = registerByte[1] #  CONFIG_REGISTER = 0x01 Point to configuration register
            self.i2c.writeto(self.addr,replaceByte,True)     # Write first byte
            return 0
  
        else : #// Return OS bit of configuration register (0-not ready, 1-conversion complete)

            return ((registerByte[0] & (1 << 7)) >> 7)

    def setLowTempC(self,temperature):
    
        # Prevent temperature from exceeding 150C or -55C
        if (temperature > 150.0):
   
            temperature = 150.0
 
        if (temperature < -55.0):
  
            temperature = -55.0
 
        #print("LowTempC = ", temperature)
        self.openPointerRegister(C_CONFIG_REGISTER)
        # Read current configuration register value
        registerByte = self.readRegister()
        extendedMode = (registerByte[1] & 0x10) >> 4 # 0 - temp data will be 12 bits
                                                     # 1 - temp data will be 13 bits
        # Convert analog temperature to digital value
        dTemperature = int(temperature / 0.0625)
        # Split temperature into separate bytes
        if (extendedMode): #// 13-bit mode
   
            replaceByte[1] = (dTemperature >> 5) & 0xFF
            replaceByte[2] = (dTemperature << 3) & 0xF8
    
        else: #// 12-bit mode
  
            replaceByte[1] = (dTemperature >> 4) & 0xFF
            replaceByte[2] = (dTemperature << 4) & 0xF0
  
        # Write to T_LOW Register
        replaceByte[0] = T_LOW_REGISTER  # write to LOW_REGISTER
        #print("writing lowTemperature = ",replaceByte)
        self.i2c.writeto(self.addr,replaceByte,True)    # Write bytes

    def setHighTempC(self,temperature):
 
        # Prevent temperature from exceeding 150C or -55C
        if (temperature > 150.0) :
   
            temperature = 150.0
 
        if (temperature < -55.0) :
  
            temperature = -55.0
 
        # Read current configuration register value
        #print("Set HighTempC = ", temperature)
        self.openPointerRegister(C_CONFIG_REGISTER)
        # Read current configuration register value
        registerByte = self.readRegister()
        extendedMode = (registerByte[1] & 0x10) >> 4 # 0 - temp data will be 12 bits
                                                     # 1 - temp data will be 13 bits
        # Convert analog temperature to digital value
        dTemperature = int(temperature / 0.0625)
        # Split temperature into separate bytes
        if (extendedMode) : #// 13-bit mode
   
            replaceByte[1] = (dTemperature >> 5) & 0xFF
            replaceByte[2] = (dTemperature << 3) & 0xF8
    
        else : #// 12-bit mode
  
            replaceByte[1] = (dTemperature >> 4) & 0xFF
            replaceByte[2] = (dTemperature << 4) & 0xF0
  
        # Write to T_HIGH Register
        replaceByte[0] = T_HIGH_REGISTER  
        #print("writing HighTemp",replaceByte)        #self.i2c.writeto(self.addr,T_HIGH_REGISTER,0)    # Point to T_HIGH
        self.i2c.writeto(self.addr,replaceByte,True)    # Write first byte
    
    def setLowTempF(self, temperature):
        temperature = (temperature - 32) * 5 / 9 # Convert temperature to C
        self.setLowTempC(temperature)            # Set T_LOW
 
    def setHighTempF(self, temperature):
        temperature = (temperature - 32) * 5 / 9 # Convert temperature to C
        self.setHighTempC(temperature)            # Set T_LOW

    def readLowTempC(self):
        #  Check if temperature should be 12 or 13 bits
        #  Change pointer address to config register (0)
        self.openPointerRegister(C_CONFIG_REGISTER)
        #  Read current configuration register value
        registerByte = self.readRegister()

        extendedMode = (registerByte[1] & 0x10) >> 4  # 0 - temp data will be 12 bits
                                                      # 1 - temp data will be 13 bits
        self.openPointerRegister(C_T_LOW_REGISTER) 
        registerByte = self.readRegister()
 
        if (registerByte[0] == 0xFF & registerByte[1] == 0xFF) :
  
            return NAN;
        
        if (extendedMode):  # 13 bit mode
     
             #combine bytes to create a signed int
            digitalTemp = ((registerByte[0]) << 5) | (registerByte[1] >> 3)
            # Temperature data can be + or -, if it should be negative,
            # convert 13 bit to 16 bit and use the 2s compliment.
            if (digitalTemp > 0xFFF):
                digitalTemp |= 0xE000
        else : #12 bit mode
         # Combine bytes to create a signed int
            digitalTemp = ((registerByte[0]) << 4) | (registerByte[1] >> 4)
            # Temperature data can be + or -, if it should be negative,
            # convert 13 bit to 16 bit and use the 2s compliment.
            if (digitalTemp > 0x7FF) :
                digitalTemp |= 0xF000
        return digitalTemp * 0.0625  #Convert digital reading to analog temperature (1-bit is equal to 0.0625 C)

    def readHighTempC(self):
        #  // Check if temperature should be 12 or 13 bits
        # // Change pointer address to config register (0)
        self.openPointerRegister(C_CONFIG_REGISTER)
        #  // Read current configuration register value
        registerByte = self.readRegister()
        extendedMode = (registerByte[1] & 0x10) >> 4  # 0 - temp data will be 12 bits
                                                      # 1 - temp data will be 13 bits
        self.openPointerRegister(C_T_HIGH_REGISTER)
        registerByte = self.readRegister()

        if (registerByte[0] == 0xFF & registerByte[1] == 0xFF) :
  
            return NAN;
        
        if (extendedMode) : # 13 bit mode
     
             #combine bytes to create a signed int
            digitalTemp = ((registerByte[0]) << 5) | (registerByte[1] >> 3)
            # Temperature data can be + or -, if it should be negative,
            # convert 13 bit to 16 bit and use the 2s compliment.
            if (digitalTemp > 0xFFF) :
                digitalTemp |= 0xE000
        else  : #12 bit mode
            # Combine bytes to create a signed int
            digitalTemp = (registerByte[0] << 4) | (registerByte[1] >> 4)
            # Temperature data can be + or -, if it should be negative,
            # convert 13 bit to 16 bit and use the 2s compliment.
            if (digitalTemp > 0x7FF) :
                digitalTemp |= 0xF000
        return digitalTemp * 0.0625  #Convert digital reading to analog temperature (1-bit is equal to 0.0625 C)

    def readLowTempF(self):
 
        return self.readLowTempC() * 9.0 / 5.0 + 32.0

    def readHighTempF(self):
    
        return self.readHighTempC() * 9.0 / 5.0 + 32.0

    def setFault (self, faultSetting):

        faultSetting = faultSetting & 3 # Make sure rate is not set higher than 3.
        #print("Fault setting = ", faultSetting)
        # Read current configuration register value
        self.openPointerRegister(C_CONFIG_REGISTER)
        # Read current configuration register value
        registerByte = self.readRegister()
        # Load new conversion rate
        replaceByte1 = registerByte[1] & 0xE7              # // Clear F0/1 (bit 3 and 4 of first byte)
        replaceByte1 |= faultSetting << 3 # // Shift new fault setting
        # Set configuration register
        replaceByte[0] = CONFIG_REGISTER
        replaceByte[1] = registerByte[0] # CONFIG_REGISTER still open
        replaceByte[2] = replaceByte1
        #print("setting fault = ",replaceByte)
        self.i2c.writeto(self.addr,replaceByte,True)     # Write first byte
    
    def setAlertMode(self,mode):
        # Read current configuration register value
        #print("alertMode = ",mode)
        self.openPointerRegister(C_CONFIG_REGISTER)
        # Read current configuration register value
        registerByte = self.readRegister()
        #  Load new conversion rate
        replaceByte0 = registerByte[0] & 0xFD       # Clear old TM bit (bit 1 of first byte)
        replaceByte0 = replaceByte0 | mode << 1  # Shift in new TM bit
             # Set configuration register
        replaceByte[0] = CONFIG_REGISTER  # Point to configuration register
        replaceByte[1] = replaceByte0 
        replaceByte[2] = registerByte[1] 
        # print("setting alertMode = ",replaceByte)
        self.i2c.writeto(self.addr,replaceByte,True)     # Write both byte
 
### END OF FILE ###
