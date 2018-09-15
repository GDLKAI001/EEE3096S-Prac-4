#!/usr/bin/python

import spidev
import time
import os
import sys
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
switch_1 = 17
switch_2 = 18
switch_3 = 27
switch_4 = 22

#Configure for pull up R
GPIO.setup(switch_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(switch_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(switch_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(switch_4, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1350000

#RPI has one bus(#0) and two devices (#0 & #1)

#Define sensor channels
channel1 = 0
channel2 = 1
channel3 = 2

#Delay(frequency)
delay = 0.5

#Define timer
timer = 0

#Define recording array
record = []

counter = 0
sense = True
#Function to convert data to V- level
def ConvertVoltage(data,places):
	voltage = (data*3.3)/float(1023)
	voltage = round (voltage,places)
	return voltage

# threaded callbacks
#Reset Timer
def callback1(channel1):
	global timer
	timer = 0
	print("\n"*100)				

#Change frequency
def callback2(channel2):
	global delay
	if (delay<2):
		delay*=2
	else:
		delay=0.5
# Stop/Start monitoring of sensors
def callback3(channel3):
	global sense
	#clear redording array
	global record
	record = []
	if (sense== True):
		sense = False
	elif(sense == False):
		sense= True

# Display readings
def callback4(channel4):
	global sense
	global record
	if (sense==True):
		if (len(record)>4):
			print('_'*47)
			print('Time        Timer          Pot    Temp   Light')
			for i in range(0,5):
				print(record[i])
				print('_'*47)
		else:
			print("Please wait for 5 readings to be recorded")

	else:
		print("Sensor  not on")

# Under a falling-edge detection, regardless od current execution
# callback function will be called
GPIO.add_event_detect(switch_1, GPIO.FALLING, callback = callback1, bouncetime = 200)
GPIO.add_event_detect(switch_2, GPIO.FALLING, callback = callback2, bouncetime = 200)
GPIO.add_event_detect(switch_3, GPIO.FALLING, callback = callback3, bouncetime = 200)
GPIO.add_event_detect(switch_4, GPIO.FALLING, callback = callback4, bouncetime = 200)

# function to read ADC data from a channel
def GetData(channel): #channel must be an integer 0-7
	adc = spi.xfer2([1,(8+channel)<<4,0]) #sending 3 bytes
	data = ((adc[1]&3) << 8) + adc[2]
	return data

#Convert data to voltage
#decplace: number of decimal places needed
def ConvertVolts(data,decplaces):
	voltage = (data*3.3)/float(1023)
	voltage = roun(volts,decplaces)
	return voltage

#Convert V to temp
def Temperature(voltage):
	tempC = int ((voltage-0.5)*100)
	return tempC

#LDR voltage to %
def Percent(voltage):
	percentage = (int(voltage/3.1*100))
	return percentage
try:
	while True:
		if (sense == True):
			#Get data
			sensor_pot = GetData (channel1)
			sensor_temp = GetData (channel2)
			sensor_LDR = GetData (channel3)
			#Convert to volts
			pot_V = ConvertVoltage(sensor_pot,2)
			temp_V = ConvertVoltage(sensor_temp,2)
			ldr_V = ConvertVoltage(sensor_LDR,2)
			#Convert to needed form
			temp = Temperature(temp_V)
			ldr_p = Percent(ldr_V)
			#add to array
			reading = (str(time.strftime("%H:%M:%S   ")) + '00:00:' + str(timer) + "     " + str(pot_V) + 'V    ' + str(temp) + 'C   ', str(ldr_p) + '%')
			record.append(reading)

			timer +=delay
			# Wait before repeating loop
			time.sleep(delay)


except KeyboardInterrupt:
	spi.close()
	GPIO.cleanup()
