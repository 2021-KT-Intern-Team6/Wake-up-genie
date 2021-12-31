#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date:2019.02.18
Example 8: 음성인식 TTS 대화 결합 예제
"""

from __future__ import print_function

import MicrophoneStream as MS
import ex1_kwstest as kws
import ex2_getVoice2Text as sst
import ex4_getText2VoiceStream as tts
import ex6 as dss
import time

import gigagenieRPC_pb2
import gigagenieRPC_pb2_grpc
from ctypes import *
import grpc


def main():
	#Example8 KWS+STT+DSS

	KWSID = ['지니야', '기가지니', '친구야', '자기야', 'wake up 지니']
	while 1:
		recog=kws.test(KWSID[0])
		if recog == 200:
			

			dss_answer = dss.queryByVoice()
								
							#time.sleep(2)
		else:
			print('KWS Not Dectected ...')

if __name__ == '__main__':
    main()
