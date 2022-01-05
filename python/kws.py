#!/usr/bin/env python
# -*- coding: utf-8 -*-
# file_name: kws.py
# file_function:
# 1. 기가지니 호출 기능

#========= Import library ===========#
from __future__ import print_function

import audioop
from ctypes import *
import RPi.GPIO as GPIO
import ktkws # KWS
import MicrophoneStream as MS
#====================================#
KWSID = ['기가지니', '지니야', '친구야', '자기야', 'wake up 지니']
RATE = 16000
CHUNK = 512

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(29, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(31, GPIO.OUT)
btn_status = False


#버튼 on/off 함수
def callback(channel):  
	print("falling edge detected from pin {}".format(channel))
	global btn_status
	if btn_status == True:
		btn_status = False
	else:
		btn_status = True
	#print(btn_status)
	return btn_status 

GPIO.add_event_detect(29, GPIO.FALLING, callback=callback, bouncetime=10)

#ALSA(Advanced Linux Sound Architectrue)의 설정으로 인해 발생하는 불필요한 에러메시지를 삭제하기 위해 Python Error Handler를 정의하는 부분
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
  dummy_var = 0
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
asound = cdll.LoadLibrary('libasound.so')
asound.snd_lib_error_set_handler(c_error_handler)


def detect():
	with MS.MicrophoneStream(RATE, CHUNK) as stream:
		audio_generator = stream.generator()
		for content in audio_generator:
			if btn_status == False:
				return 500
			rc = ktkws.detect(content)
			rms = audioop.rms(content,2)
			#print('audio rms = %d' % (rms))
			if (rc == 1):
				print(8)
				MS.play_file("../data/sample_sound.wav")
				print(9)
				return 200
"""
def btn_detect():
	global btn_status
	with MS.MicrophoneStream(RATE, CHUNK) as stream:
		audio_generator = stream.generator()

		for content in audio_generator:
			#GPIO.output(31, btn_status)
			rc = ktkws.detect(content)
			rms = audioop.rms(content,2)
			#print('audio rms = %d' % (rms))
			#GPIO.output(31, GPIO.LOW)
			if (btn_status == True):
				rc = 1
				btn_status = False			
			if (rc == 1):
				GPIO.output(31, GPIO.HIGH)
				#MS.play_file("../data/sample_sound.wav")
				return 200
"""
#기가지니 호출 대기
def test(key_word = '졸려'):
	rc = ktkws.init("../data/kwsmodel.pack")
	print ('init rc = %d' % (rc))
	rc = ktkws.start()
	print ('start rc = %d' % (rc))
	print ('\n호출어를 불러보세요~\n')
	ktkws.set_keyword(KWSID.index(key_word))
	rc = detect()
	print ('detect rc = %d' % (rc))
	print ('\n\n호출어가 정상적으로 인식되었습니다.\n\n')
	ktkws.stop()
	return rc

"""
def btn_test(key_word = '기가지니'):
	global btn_status
	rc = ktkws.init("../data/kwsmodel.pack")
	print ('init rc = %d' % (rc))
	rc = ktkws.start()
	print ('start rc = %d' % (rc))
	print ('\n버튼을 눌러보세요~\n')
	ktkws.set_keyword(KWSID.index(key_word))
	rc = btn_detect()
	print ('detect rc = %d' % (rc))
	print ('\n\n호출어가 정상적으로 인식되었습니다.\n\n')
	ktkws.stop()
	return rc
"""
def main():
	#test()
	GPIO.output(31, btn_status)
	return(btn_status)

if __name__ == '__main__':
	main()
