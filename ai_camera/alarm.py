# file_name: alarm.py
# file_function: 졸음의 단계에 따라 다른 알람을 울려줌

#========= Import library ===========#
import pygame
#===================================#

# function_name: select_alarm
# input: 졸음의 강도(0, 1, 2)
# function: result를 받아서 강도별로 설정된 알람을 울려주는 함수

def select_alarm(result) :
    if result == 0: #졸음의 강도가 0일때 아래의 파일을 울림
        sound_alarm("power_alarm.wav")
    elif result == 1 : #졸음의 강도가 1일때 아래의 파일을 울림
        sound_alarm("nomal_alarm.wav")
    else : #졸음의 강도가 2일때 아래의 파일을 울림
        sound_alarm("short_alarm.mp3")

# function_name: sound_alarm
# input: 울리고자 하는 알람의 경로
# function: pygame을 사용하여 알람을 울려주는 함수

def sound_alarm(path) :
    pygame.mixer.init()
    pygame.mixer.music.load(path) #path경로에 있는 알람을 울려줌
    pygame.mixer.music.set_volume(0.7)
    pygame.mixer.music.play()
