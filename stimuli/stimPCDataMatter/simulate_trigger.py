from time import sleep
from pyKey import *

TR=1
SCANNER_TRIGGER = '5'

for i in range(800):

	press(SCANNER_TRIGGER)
	sleep(TR)