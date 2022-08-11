from i2c102temp import T102
from machine import Pin, I2C
import time


ALERT_PIN = 0x00


sensor = T102()
if ( sensor.init() != 0):
    print("Cannot connect to TMP102")
    print("Is the board connected? Is the device ID correct?")
else:
    print ("Connected to board")
    # set T_HIGH, the upper limit to trigger the alert on
    # first read HighTemp
    #print("High before set : "+str(sensor.readHighTempF()))
    time.sleep(.25)
    sensor.setHighTempF(95.0)
    time.sleep(.25)
    print("High temp set at : "+str(sensor.readHighTempF()))
    #sensor.setHighTempC(29.4)
    # set T_LOW, the upper limit to shut turn off the alert
    #print("Low before set : "+str(sensor.readLowTempF()))
    sensor.setLowTempF(81.0)
    #sensor.setLowTempC(26.67)
    time.sleep(.25)
    print("Low temp set at : "+str(sensor.readLowTempF()))
    time.sleep(.25)
    sensor.setFault(0)  # Trigger alarm immediately
    time.sleep(.1)
    sensor.setAlertPolarity(1)  #// Active HIGH
    time.sleep(.1)
    sensor.setAlertMode(0)  #// Comparator Mode
    time.sleep(.1)
    # set the Conversion Rate (how quickly the sensor gets a new reading)
    # 0-3: 0:0.25Hz, 1:1Hz, 2:4Hz, 3:8Hz
    sensor.setConversionRate(1)
    time.sleep(.1)
    # set Extended Mode.
    # 0:12-bit Temperature(-55C to +128C) 1:13-bit Temperature(-55C to +150C
    sensor.setExtendedMode(0)
    time.sleep(.1)

    while (1):
        sensor.wakeup()
        temperature = sensor.readTempF()
        if (sensor.alertPin != None):
            alertPinState = sensor.alertPin.value()
            alertRegisterState = sensor.alert()
            print("Alert Pin = "+str(alertPinState))
            print("Alert Register = "+str(alertRegisterState))       
        print ("Temperature = "+str(temperature)+'F')
        sensor.sleep()
        time.sleep(5)
        
        
    