#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Example 6: STT + Dialog - queryByVoice"""

from __future__ import print_function

import grpc
import time
import gigagenieRPC_pb2
import gigagenieRPC_pb2_grpc
import MicrophoneStream as MS
import user_auth as UA
import os
### STT
import ex4_getText2VoiceStream as tts
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

def queryByVoice():
	
	
	
	print ("듣고 있는 중......\n")
	request = generate_request()
	Text = ''
	response = stub.queryByVoice(request)
	if response.resultCd == 200:
		Text = response.uword
		
	if Text == '졸려':
		a=random.randrange(1,10)
		b=random.randrange(1,10)
		
		test = readNumber(a) + ' 곱하기 ' + readNumber(b) + '--'
		#test = '1234321'
		tts.getText2VoiceStream(test, "result_mesg.wav")
		MS.play_file("result_mesg.wav")
		
		time.sleep(0.5)
		
		print ("듣고 있는 중......\n")
		request = generate_request()
		resultText = ''
		response = stub.queryByVoice(request)
		if response.resultCd == 200:
			resultText = response.uword
			
			if resultText == '':
				print('질의한 내용이 없습니다.\n\n\n')
			else:
				print("답한 내용: %s" % (resultText))
				
				"""
				text_split = resultText.split(' ')
				f = False
				
				for t in text_split:
					answer = korean2num.decode(t)
					print(answer)
				
				#answer=int(input())
					if a*b == answer and f == False:
						print("정답입니다")
						tts.getText2VoiceStream('정답입니다', "result_mesg.wav")
						MS.play_file("result_mesg.wav")
						f = True
				"""
				if resultText.find(str(a*b)) == 0 or resultText.find(readNumber(a*b)) == 0:
					print("정답입니다")
					tts.getText2VoiceStream('정답입니다', "result_mesg.wav")
					MS.play_file("result_mesg.wav")
				
				#if f == False:
				else:
					print("오답입니다. 정답은", readNumber(a*b),"입니다")
					tts.getText2VoiceStream('오답입니다', "result_mesg.wav")
					MS.play_file("result_mesg.wav")
									
			
			
			
			return resultText
			#return response.uword
			"""
			for a in response.action:
				response = a.mesg
				parsing_resp = response.replace('<![CDATA[', '')
				print(parsing_resp)
				parsing_resp = parsing_resp.replace(']]>', '')
				print(parsing_resp)
				resultText = parsing_resp
				print(resultText)
				print("\n질의에 대한 답변: " + parsing_resp +'\n\n\n')
			"""

		else:
			print("\n\nresultCd: %d\n" % (response.resultCd))
			print("정상적인 음성인식이 되지 않았습니다.")
			return ''
		

def main():
	queryByVoice(8,6)
	#print(result)
	#tts.getText2VoiceStream(result, "result_mesg.wav")
	#MS.play_file("result_mesg.wav")
	#print(tts_result)

	'''
	time.sleep(5)
	tts_result = tts.getText2VoiceStream(result, "result_mesg.wav")
	time.sleep(0.5)
	'''
if __name__ == '__main__':
	while 1:
		main()
