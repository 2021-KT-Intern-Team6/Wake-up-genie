from __future__ import print_function
# file_name: project_sensortoge.py
# file_function:
# 1. 온도, 이산화탄소 센서에서 값을 실시간으로 받음
# 2. 온도, 이산화탄소 값이 특정 값 이상일 때 음성 알림
#========= Import library ===========#
import grpc
import gigagenieRPC_pb2
import gigagenieRPC_pb2_grpc
import MicrophoneStream as MS
import user_auth as UA
import kws
import tts
import time
import Adafruit_DHT as dht
import os
import serial
from ctypes import *
from threading import Thread
#=====================================#

HOST = 'gate.gigagenie.ai'
PORT = 4080
port = '/dev/ttyUSB0'
brate = 9600
cmd = 'temp'

#ALSA(Advanced Linux Sound Architectrue)의 설정으로 인해 발생하는 불필요한 에러메시지를 삭제하기 위해 Python Error Handler를 정의하는 부분
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
  dummy_var = 0
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
asound = cdll.LoadLibrary('libasound.so')
asound.snd_lib_error_set_handler(c_error_handler)

#humidity = 0.0 
temperature = 0.0 #온도 값 자료공간 생성

def getText2VoiceStream(inText,inFileName): # 변환할 텍스트와 변환된 파일의 명을 받아서 음성 파일을 생성하는 함수 

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
		
seri = serial.Serial(port, baudrate = brate, timeout = None) #아두이노, 라즈베리파이 씨리얼 연결 (아두이노 센서 값이 아날로그로 나와 디지털 값으로 변환하기 위함)
seri.write(cmd.encode()) #센서 값 전송

def read_sensor(): # 온도 센서 값을 읽기 위한 함수 
	global temperature
	while True:
		humidity, temperature = dht.read_retry(11, 4)
		print('temp : ' + str(temperature))
		#print('humi : ' + str(humidity))
		
	
def getTemp(): # 온도 센서 값을 얻기 위한 함수
	global temperature
	return temperature
	
		
def main():
	
	
	humidity, temperature = dht.read_retry(11, 4)
	print(temperature) # 온도 값 출력 (정상 작동하는지 확인하는 용도)
	if seri.in_waiting !=0 :   # 아두이노 센서 값을 정상적으로 불러왔는 지 확인
	#time.sleep(2)

		content = seri.readline() # 불러온 아두이노 센서 값 저장   
		
		x=float(content[:-2].decode()) # 아두이노 센서 값 변수에 저장
		
		print(x) # 아두이노 센서 값 출력(정상 작동 확인 용)
		
		
		if x < 50.0 and temperature <26: # 이산화탄소 농도와 온도 값이 높을 경우의 음성 출력

			output_file = "test.wav"
			getText2VoiceStream("이산화탄소 농도가 높습니다 환기가 필요합니다", output_file)
			MS.play_file(output_file)
			
		if x < 50.0 and temperature > 26: # 이산화탄소 농도만 높을 경우의 음성 출력
			
			output_file = "test.wav"
			getText2VoiceStream("이산화탄소 농도와 실내온도가 높습니다 졸음운전 주의바랍니다", output_file)
			MS.play_file(output_file)
						
		if x > 50.0 and temperature > 26: # 온도만 높을 경우의 음성 출력
			
			output_file = "test.wav"
			getText2VoiceStream("이십육도이상입니다 졸음운전 주의바랍니다", output_file)
			MS.play_file(output_file)
			
		
		
		
#t = Thread(target=read_sensor)  # 온도센서 쓰레드
#t.deamon = True
#t.start()
	

if __name__ == '__main__':
	main()
