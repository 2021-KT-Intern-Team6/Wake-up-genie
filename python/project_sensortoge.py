from __future__ import print_function


import grpc
import gigagenieRPC_pb2
import gigagenieRPC_pb2_grpc
import MicrophoneStream as MS
import user_auth as UA
import kws
import tts
import Adafruit_DHT as dht
import time
import MicrophoneStream as MS
import os
import serial
from ctypes import *

HOST = 'gate.gigagenie.ai'
PORT = 4080
port = '/dev/ttyUSB0'
brate = 9600
cmd = 'temp'

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
  dummy_var = 0
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
asound = cdll.LoadLibrary('libasound.so')
asound.snd_lib_error_set_handler(c_error_handler)

def getText2VoiceStream(inText,inFileName):

	channel = grpc.secure_channel('{}:{}'.format(HOST, PORT), UA.getCredentials())
	stub = gigagenieRPC_pb2_grpc.GigagenieStub(channel)

	message = gigagenieRPC_pb2.reqText()
	message.lang=0
	message.mode=0
	message.text=inText
	writeFile=open(inFileName,'wb')
	for response in stub.getText2VoiceStream(message):
		if response.HasField("resOptions"):
			print ("\n\nResVoiceResult: %d" %(response.resOptions.resultCd))
		if response.HasField("audioContent"):
			print ("Audio Stream\n\n")
			writeFile.write(response.audioContent)
	writeFile.close()
	return response.resOptions.resultCd
		
		
def main():
	
	seri = serial.Serial(port, baudrate = brate, timeout = None)
	seri.write(cmd.encode())
	humidity, temperature = dht.read_retry(11, 4)
	
	if seri.in_waiting !=0 :   # conect with adu
		#time.sleep(2)
		#content = seri.readline() # save value  
		#x=float(content[:-2].decode())
		x = 80.0
		print(x)
		print(temperature)
		if x < 85.0 and temperature <5.0: 

			MS.play_file("test5.wav")
			#time.sleep(10)
			
		if x < 85.0 and temperature >= 5.0:
			MS.play_file("test6.wav")
			#time.sleep(10)
						
		if x >= 85.0 and temperature >= 5.0:
			MS.play_file("test7.wav")
			#time.sleep(10)

			
		


if __name__ == '__main__':
	main()
