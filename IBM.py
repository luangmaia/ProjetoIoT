# Danilo de Moura Chenchi - 511480
# Jonathan André Nunes da Silva - 489557
# Luan Gustavo Maia Dias - 587737
# Matheus Gomes Barbieri - 408344
#!/usr/bin/env python
import paho.mqtt.client as mqtt
import sys
import time
from threading import Thread

from libsoc import gpio
from libsoc_zero.GPIO import Tilt
import spidev
from libsoc import gpio
from time import sleep

import ibmiotf.device

organization = "2yutff"
deviceType = "DragonBoard"
deviceId = "1"
authMethod = "token"
authToken = "Z?37?oq(+0*ER8JNdC"

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=10000
spi.mode = 0b00
spi.bits_per_word = 8
channel_select_temperatura=[0x01, 0xA0, 0x00]
channel_select_luminosidade=[0x01, 0x80, 0x00]

deviceOptions = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}
deviceCli = ibmiotf.device.Client(deviceOptions)

deviceCli.connect()

tiltVal = 0
tilt = Tilt('GPIO-A')

class Th_tilt(Thread):

	def __init__ (self):
		Thread.__init__(self)

	def run(self):
		global tiltVal
		while True:
			tilt.wait_for_tilt()
			tiltVal = 1
			sleep(5)

def read_analog(gpio_cs, select):
	gpio_cs.set_high()
	sleep(0.00001)
	gpio_cs.set_low()
	
	if (select == 1):
		rx = spi.xfer(channel_select_temperatura)
	elif (select == 2):
		rx = spi.xfer(channel_select_luminosidade)

	gpio_cs.set_high()

	adc_value = (rx[1] << 8) & 0b1100000000
	adc_value = adc_value | (rx[2] & 0xff)

	return adc_value

def send_message(msg, msg2, tiltv):
	data = { 'temp' : msg}
	deviceCli.publishEvent("temp", "json", data, qos=1)
	data = { 'luminosidade' : msg2}
	deviceCli.publishEvent("luminosidade", "json", data, qos=1)
	data = { 'tilt' : tiltv}
	deviceCli.publishEvent("tilt", "json", data, qos=1)
	print(" [x] Sent 'Tilt: %d'" % tiltVal)

if __name__ == '__main__':
	gpio_cs = gpio.GPIO(18, gpio.DIRECTION_OUTPUT)

	with gpio.request_gpios([gpio_cs]):
		seconds = 0

		threadTilt = Th_tilt()
		threadTilt.start()

		while True:
			adc_value_temp = read_analog(gpio_cs, 1)
			adc_value_pot = read_analog(gpio_cs, 2)

			temperatura = (((adc_value_temp*5)/1024)-0.5)*100
			luminosidade = adc_value_pot
			print(" [x] Sent 'Temperatura: %d Celsius'" % temperatura)
			print(" [x] Sent 'Luminosidade: %d'" % luminosidade)
			send_message(temperatura, luminosidade, tiltVal)
			tiltVal = 0

			sleep(5)
			seconds = seconds + 5

	connection.close()