# Danilo de Moura Chenchi - 511480
# Jonathan André Nunes da Silva - 489557
# Luan Gustavo Maia Dias - 587737
# Matheus Gomes Barbieri - 408344
#!/usr/bin/env python
#import paho.mqtt.client as mqtt
import sys
import time

#import spidev
import random
#from libsoc import gpio
from time import sleep

import ibmiotf.device

organization = "2yutff"
deviceType = "DragonBoard"
deviceId = "1"
authMethod = "token"
authToken = "Z?37?oq(+0*ER8JNdC"
'''
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=10000
spi.mode = 0b00
spi.bits_per_word = 8
channel_select_temperatura=[0x01, 0xA0, 0x00]
channel_select_potenciometro=[0x01, 0x80, 0x00]
'''
deviceOptions = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}
deviceCli = ibmiotf.device.Client(deviceOptions)

deviceCli.connect()
'''
def read_analog(gpio_cs, select):
	gpio_cs.set_high()
	sleep(0.00001)
	gpio_cs.set_low()
	
	if (select == 1):
		rx = spi.xfer(channel_select_temperatura)
	elif (select == 2):
		rx = spi.xfer(channel_select_potenciometro)

	gpio_cs.set_high()

	adc_value = (rx[1] << 8) & 0b1100000000
	adc_value = adc_value | (rx[2] & 0xff)

	return adc_value
'''
def send_message(msg, msg2):
	data = { 'temp' : msg}
	deviceCli.publishEvent("temp", "json", data, qos=1)
	data = { 'slider' : msg2}
	deviceCli.publishEvent("slider", "json", data, qos=1)

if __name__ == '__main__':
#	gpio_cs = gpio.GPIO(18, gpio.DIRECTION_OUTPUT)

#	with gpio.request_gpios([gpio_cs]):
	seconds = 0
	while True:
#			adc_value_temp = read_analog(gpio_cs, 1)
#			adc_value_pot = read_analog(gpio_cs, 2)

#			temperatura = (((adc_value_temp*5)/1024)-0.5)*100
#			potenciometro = adc_value_pot
		temperatura = random.choice([20,21,22,23,24,25,26,27,28,29,30])
		potenciometro = random.choice([1,2,3,4,5,6,7,8,9,10])
		print(" [x] Sent 'Temperatura: %d Celsius'" % temperatura)
		print(" [x] Sent 'Potenciometro: %d'" % potenciometro)
		send_message(temperatura, potenciometro)

		sleep(5)
		seconds = seconds + 5

	connection.close()