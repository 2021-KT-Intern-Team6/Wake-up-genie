#!/usr/bin/env python
# -*- coding: utf-8 -*-

# file_name: ninenine.py
# file_function:
# 1. 구구단


from __future__ import print_function

import grpc
import time
import gigagenieRPC_pb2
import gigagenieRPC_pb2_grpc
import MicrophoneStream as MS
import user_auth as UA
import os
### STT
import tts
import audioop
from ctypes import *
import korean2num
import random

RATE = 16000
CHUNK = 512

HOST = 'gate.gigagenie.ai'
PORT = 4080

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
  dummy_var = 0
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
asound = cdll.LoadLibrary('libasound.so')
asound.snd_lib_error_set_handler(c_error_handler)

channel = grpc.secure_channel('{}:{}'.format(HOST, PORT), UA.getCredentials())
stub = gigagenieRPC_pb2_grpc.GigagenieStub(channel)

def generate_request():
	with MS.MicrophoneStream(RATE, CHUNK) as stream:
		audio_generator = stream.generator()
		messageReq = gigagenieRPC_pb2.reqQueryVoice()
		messageReq.reqOptions.lang=0
		messageReq.reqOptions.userSession="1234"
		messageReq.reqOptions.deviceId="aklsjdnalksd"
		yield messageReq
		for content in audio_generator:
			message = gigagenieRPC_pb2.reqQueryVoice()
			message.audioContent = content
			yield message
			rms = audioop.rms(content,2)


#============================= 숫자 -> 한글 숫자 ================================#			
def readNumber(n):
	units = [''] + list('십백천')
	nums = '일이삼사오육칠팔구'
	result=[]
	i=0
	while n>0:
		n, r = divmod(n,10)
		if r>0:
			result.append(nums[r-1]+units[i])
		i +=1
	return ''.join(result[::-1])
	
#============================= 구구단 ================================#	
def ninenine():
	# random을 통한 곱셈값 
	a=random.randrange(2,10)
	b=random.randrange(2,10)
	
	# 발화
	test = readNumber(a) + ' 곱하기 ' + readNumber(b) + '는?'
	tts.getText2VoiceStream(test, "result_mesg.wav")
	MS.play_file("result_mesg.wav")
	
	time.sleep(0.5)
	
	# 답 듣기
	print ("듣고 있는 중......\n")
	request = generate_request()
	resultText = ''
	response = stub.queryByVoice(request)
	if response.resultCd == 200:
		resultText = response.uword
		
		if resultText == '':#답한 내용이 없음
			print('답한 내용이 없습니다.\n\n\n')
		else:
			print("답한 내용: %s" % (resultText))

			#답이 맞는경우
			if resultText.find(str(a*b)) == 0 or resultText.find(readNumber(a*b)) == 0:
				print("정답입니다")
				tts.getText2VoiceStream('정답입니다', "result_mesg.wav")
				MS.play_file("result_mesg.wav")
			
			#답이 틀린경우
			else:
				print("오답입니다. 정답은", readNumber(a*b),"입니다")
				tts.getText2VoiceStream('오답입니다', "result_mesg.wav")
				MS.play_file("result_mesg.wav")
				ninenine()

	#답한 내용이 없음
	else:
		print("\n\nresultCd: %d\n" % (response.resultCd))
		print("정상적인 음성인식이 되지 않았습니다.")


def queryByVoice():
	
	print ("듣고 있는 중......\n")
	request = generate_request()
	Text = ''
	response = stub.queryByVoice(request)
	if response.resultCd == 200:
		Text = response.uword
		
	if Text.find('졸려') == 0 or Text.find('도와줘') == 0:
		ninenine() #구구단
		

def main():
	queryByVoice(8,6)

if __name__ == '__main__':
	while 1:
		main()
