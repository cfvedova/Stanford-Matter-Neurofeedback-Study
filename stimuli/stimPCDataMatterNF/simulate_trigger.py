from time import sleep
from pyKey import *

TR=0.2
SCANNER_TRIGGER = '5'

for i in range(800):

	press(SCANNER_TRIGGER)
	sleep(TR)