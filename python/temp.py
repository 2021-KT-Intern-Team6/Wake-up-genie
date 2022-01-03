#temp.py

import datetime

import Adafruit_DHT as dht



while True : 
	h,t = dht.read_retry(dht.DHT11,4)

 

	print (h)

	print (t)	
