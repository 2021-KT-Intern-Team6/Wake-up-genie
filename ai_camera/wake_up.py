# file_name: wake_up.py
# file_function:
# 1. 눈깜빡임 쓰레드 실행
# 2. 구구단 쓰레드 실행


import sys
from threading import Thread

sys.path.append('/home/pi/Wake_up_genie/python')
print(sys.path)

import call_genie as cg
import ai_eye_blink as eb




def main():

	t = Thread(target=cg.main) #구구단 쓰레드
	th = Thread(target=eb.main) # 눈깜빡임 쓰레드
	t.deamon = True
	th.deamon = True
	t.start() #구구단 쓰레드 실행
	th.start() # 눈깜빡임 쓰레드



if __name__ == '__main__':
	main()
