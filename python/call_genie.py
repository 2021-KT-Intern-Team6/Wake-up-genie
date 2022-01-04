#!/usr/bin/env python
# -*- coding: utf-8 -*-

# file_name: call_genie.py
# file_function:
# 1. Ai Makers 호출

from __future__ import print_function

import kws
import ninenine as nn

def main():
	# KWS+STT+구구단

	KWSID = ['지니야', '기가지니', '친구야', '자기야', 'wake up 지니']
	while 1:
		if kws.main() == True:
			recog=kws.test(KWSID[0])
			if recog == 200:
				dss_answer = nn.queryByVoice()
			else:
				print('KWS Not Dectected ...')

if __name__ == '__main__':
    main()
