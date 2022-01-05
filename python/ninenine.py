#!/usr/bin/env python
# -*- coding: utf-8 -*-


#========= Import library ===========#
from __future__ import print_function

import grpc
import time
import gigagenieRPC_pb2
import gigagenieRPC_pb2_grpc
import MicrophoneStream as MS
import project_sensortoge as ps
import ex2_getVoice2Text as stt
import user_auth as UA
import os
### STT
import tts
import audioop
from ctypes import *
import korean2num
import random
#====================================#
RATE = 16000
CHUNK = 512

HOST = 'gate.gigagenie.ai'
PORT = 4080

#ALSA(Advanced Linux Sound Architectrue)의 설정으로 인해 발생하는 불필요한 에러메시지를 삭제하기 위해 Python Error Handler를 정의하는 부분
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
  dummy_var = 0
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
asound = cdll.LoadLibrary('libasound.so')
asound.snd_lib_error_set_handler(c_error_handler)

channel = grpc.secure_channel('{}:{}'.format(HOST, PORT), UA.getCredentials())
stub = gigagenieRPC_pb2_grpc.GigagenieStub(channel)


#사용자 음성 인식을 위한 대기 및 인식 후 비교함수
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

#숫자를 한글로 바꿔주는 함수			
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
	
def ninenine(): #구구단 발화 함수
	a=random.randrange(2,10) # 2~10 숫자 랜덤 선택
	b=random.randrange(2,10) # 2~10 숫자 랜덤 선택
	
	test = readNumber(a) + ' 곱하기 ' + readNumber(b) + '는?' # 구구단 발화 할 텍스트 변수 저장
	tts.getText2VoiceStream(test, "result_mesg.wav") # 텍스트 내용 오디오 파일로 변환
	MS.play_file("result_mesg.wav") # 오디오 파일 재생
	
	time.sleep(0.5)
	
	print ("듣고 있는 중......\n")
	request = generate_request() #음성 인식 대기
	resultText = '' #음성 저장
	response = stub.queryByVoice(request) #음성 분석
	if response.resultCd == 200: #음성이 인식 되었다면
		resultText = response.uword #음성을 텍스트로 변환 
		
		if resultText == '': #말을 안했을 경우 
			print('질의한 내용이 없습니다.\n\n\n')
		else: #말을 했을 경우 내용 출력
			print("답한 내용: %s" % (resultText))

			#구구단 정답 맞췄을 경우
			if resultText.find(str(a*b)) == 0 or resultText.find(readNumber(a*b)) == 0: 
				print("정답입니다")
				tts.getText2VoiceStream('정답입니다', "result_mesg.wav")
				MS.play_file("result_mesg.wav")
			#구구단 정답 틀렸을 경우
			else:
				print("오답입니다. 정답은", readNumber(a*b),"입니다")
				tts.getText2VoiceStream('오답입니다', "result_mesg.wav")
				MS.play_file("result_mesg.wav")
				ninenine() # 틀렸을 경우는 구구단 재실행

	#말을 안하거나 인식 못했을 경우
	else:
		print("\n\nresultCd: %d\n" % (response.resultCd))
		print("정상적인 음성인식이 되지 않았습니다.")
		tts.getText2VoiceStream('못 알아들었습니다.', "result_mesg.wav")
		MS.play_file("result_mesg.wav")

#현재 온도를 발화하기 위한 함수
def TempVoice(): 
	
	test = '현재 온도는 ' + str(ps.getTemp()) + '도 입니다.'
	tts.getText2VoiceStream(test, "result_mesg.wav")
	MS.play_file("result_mesg.wav")
	
#서비스 실행을 위한 함수
def queryByVoice():
	
	
	
	print ("듣고 있는 중......\n")
	request = generate_request() #음성 대기
	Text = '' #음성 저장

	response = stub.queryByVoice(request) #음성 분석
	if response.resultCd == 200 or response.resultCd == 201: #음성 발화 혹은 발화가 끝났을 경우
		Text = response.uword #음성 택스트 변환 
		print(Text) #음성 텍스트 출력
	
	#졸려 혹은 도와줘가 포함된 문장을 말할 경우 구구단 실행	
	if Text.find('졸려') == 0 or Text.find('도와줘') == 0:
		ninenine()
		
	#상태가 포함된 문장을 말할경우 현재온도를 알려줌
	elif Text.find('상태') == 0:
		TempVoice()
	
	#그 밖에 인식을 못했을 경우 	
	else :
		print("정상적인 음성인식이 되지 않았습니다.")
		tts.getText2VoiceStream('못 알아들었습니다.', "result_mesg.wav")
		MS.play_file("result_mesg.wav")
	


		

def main():
	queryByVoice()
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
