#!/usr/bin/env python
# -*- coding: utf-8 -*-

# file_name: ai_eye_blink.py
# file_function:
# 1. 카메라로 실시간으로 데이터를 받음
# 2. 얼굴에서 눈을 감지
# 3. 눈을 떴는지 감았는지 check
# 4. 졸음인지 아닌지 check
# 5. 알람을 울림
# 6. 옵습도에 따른 알림
#========= Import library ===========#
import kws
import cv2, dlib
from tensorflow import keras
import numpy as np
from imutils import face_utils
import timeit
import knn_model as km
import alarm
from threading import Thread
import project_sensortoge as ps
import time
#===================================#




def main():
  #=================================변수선언 및 초기화====================================#

  EYE_AR_THRESH = 0.3 #눈감음의 척도: 눈의 종횡비의 마지노선
  EYE_AR_CONSEC_FRAMES = 8 #졸음을 판단하는 frame수 (27프레임 이상 눈을 감고 있으면 존다고 판단)

  COUNTER = 0 #frame수를 카운트하는 변수

  closed_eyes_time = [] #눈을 감고 있던 시간이 저장될 list
  TIMER_FLAG = False #눈을 감는 시간을 측정하는 'start_closing' 변수를 활성화하기 위한 플래그
  ALARM_FLAG = False #알람이 트리거된 적이 있는지 확인하는 플래그

  ALARM_COUNT = 0 #총 알람이 울린 횟수
  RUNNING_TIME = 0 #알람이 계속해서 꺼지지 않도록 하는 변수

  PREV_TERM = 0 #알람이 울릴 때까지 눈을 뜨고 있는 시간을 측정하는 변수

  test_data = [] # KNN모델을 사용하여 정답 예측에 input으로 사용되는 test_data list
  result_data = [] #KNN모델 예측 결과 list

  power, nomal, short = km.start(25)
  IMG_SIZE = (34, 26) #이미지 사이즈 설정

  SENSOR_FRAME = 0
  RINGING_FLAG = False

  #======================함수정의========================#

  def check_frm(prev_time):
    cur_time = time.time()
    one_loop_time= cur_time - prev_time
    prev_time = cur_time
    fps = 1/one_loop_time
    return prev_time, fps


  # function_name: crop_eye
  # input: img, eye_points
  # output: eye_img, eye_rect (눈이미지, 눈이들어있는 상자 좌표)
  # function: 얼굴이 있는 이미지에서 눈이 있는 부분의 상자 좌표를 반환

  def crop_eye(img, eye_points):
    x1, y1 = np.amin(eye_points, axis=0)
    x2, y2 = np.amax(eye_points, axis=0)
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

    w = (x2 - x1) * 1.2
    h = w * IMG_SIZE[1] / IMG_SIZE[0]

    margin_x, margin_y = w / 2, h / 2

    min_x, min_y = int(cx - margin_x), int(cy - margin_y)
    max_x, max_y = int(cx + margin_x), int(cy + margin_y)

    eye_rect = np.rint([min_x, min_y, max_x, max_y]).astype(np.int)
    eye_img = gray[eye_rect[1]:eye_rect[3], eye_rect[0]:eye_rect[2]]

    return eye_img, eye_rect

  #========================START MAIN===========================#

  #dlib를 사용하여 얼굴탐색 & dlib에서 사용할 shape predictor의 dat파일을 다운로드
  detector = dlib.get_frontal_face_detector()
  predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat/shape_predictor_68_face_landmarks.dat')

  #학습시킨 모델을 불러온 후 모델의 구조 확인
  model = keras.models.load_model('models/2022_01_01_21_49_51.h5')
  model.summary()

  #==================모델에 사용할 데이터 전처리 과정==================#

  cap = cv2.VideoCapture(0) #카메라 실행
  prev_time = time.time()
  while cap.isOpened(): #카메라가 실행되었다면
        
    if kws.main() == True:#스위치를 이용한 온오프
      ret, img_ori = cap.read() #비디오의 한 프레임 씩 읽어오기 제대로 프레임을 읽으면 ret값이 True, 실패하면 False, fram = 읽은 프레임
      SENSOR_FRAME += 1
      if not ret: #제대로 프레임을 읽어오지 못했다면 while문 탈출해서 카메라 실행 중지
        break

      img_ori = cv2.resize(img_ori, dsize=(0, 0), fx=0.5, fy=0.5) #x축과 y축 방향으로 스케일 비율 조정
      # img_ori: 입력 영상 / dsize=(0,0) => fx와 fy값을 이용하여 설정하겠다는 의미

      img = img_ori.copy() #이미지 복사
      gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #gray scailing한 img를 gray에 저장

      faces = detector(gray) #gray scail 이미지에서 얼굴을 인식
      
      #prev_time, fps = check_frm(prev_time)
      #print('frame count: ' + str(fps))
      
      # 얼굴 감지에 대한 루프
      for face in faces:

        shapes = predictor(gray, face) # 얼굴 영역의 얼굴 랜드마크를 결정한 다음
        shapes = face_utils.shape_to_np(shapes) # 얼굴 랜드마크(x, y) 좌표를 NumPy로 변환

        eye_img_l, eye_rect_l = crop_eye(gray, eye_points=shapes[36:42]) #왼쪽눈부분만 crop => 왼쪽눈 이미지와 사각형 좌표 반환
        eye_img_r, eye_rect_r = crop_eye(gray, eye_points=shapes[42:48]) #오른쪽 눈부분만 crop => 오른쪽눈 이미지와 사각형 좌표 반환

        #눈 이미지크기 재설정
        eye_img_l = cv2.resize(eye_img_l, dsize=IMG_SIZE)
        eye_img_r = cv2.resize(eye_img_r, dsize=IMG_SIZE)
        eye_img_r = cv2.flip(eye_img_r, flipCode=1) #오른쪽 눈은 좌우반전

        #눈의 이미지를 1차원 배열로 reshape하여 0-1사이의 숫자로 바꿔줌
        eye_input_l = eye_img_l.copy().reshape((1, IMG_SIZE[1], IMG_SIZE[0], 1)).astype(np.float32) / 255.
        eye_input_r = eye_img_r.copy().reshape((1, IMG_SIZE[1], IMG_SIZE[0], 1)).astype(np.float32) / 255.

        #====================데이터 전처리 과정 끝! 모델이 결과를 예측===================#

        #불러온 CNN모델로 결과예측
        pred_l = model.predict(eye_input_l)
        pred_r = model.predict(eye_input_r)

        #===============================예측된 결과로 졸음을 판별하는 과정=======================================#

        # visualize
        state_l = '%.1f' if pred_l > 0.1 else '%.1f'
        state_r = '%.1f' if pred_r > 0.1 else '%.1f'

        state_l = state_l % pred_l
        state_r = state_r % pred_r

        #eye_open_close = 학습된 결과로 두 눈을 감았는지 떴는지를 알려주는 수치
        eye_open_close = (float(state_l) + float(state_r)) / 2.0
        print(COUNTER)

        #눈을 감으면
        if eye_open_close < EYE_AR_THRESH:
          if not TIMER_FLAG: # 이전에 타이머가 시작이 안되었으면 (=이전에 눈을 뜨고 있었으면)
            start_closing = timeit.default_timer()  # 눈을 감기 시작한 시간 check
            TIMER_FLAG = True # TIMER_FLAG를 True로 설정해서 이전에 눈을 감았다는 것을 알려줌
          COUNTER += 1 #눈을 감은 frame수를 의미하는 COUNTER를 +1

          if COUNTER >= EYE_AR_CONSEC_FRAMES: # 일정 프레임이상 눈을 감은게 인지되면 => 졸음이라고 인지하면
            mid_closing = timeit.default_timer()  # 인지하는 시점에서 시간을 한번 더 저장한다.
            closing_time = round((mid_closing - start_closing), 3)  # 눈을 감고 있던 시간을 계산
            if closing_time >= RUNNING_TIME: #running_time => 알람이 꺼지지 않게 해주는 변수(알람의 단계를 설정하는 변수...?)
              if RUNNING_TIME == 0: #처음 졸음이라고 인지했을때
                CUR_TERM = timeit.default_timer()
                OPENED_EYES_TIME = round((CUR_TERM - PREV_TERM), 3)
                PREV_TERM = CUR_TERM
                RUNNING_TIME = 1.75 #..?

              RUNNING_TIME += 2 # 뭔가 알람의 단계를 설정하는 것과 관계있는 변수
              ALARM_FLAG = True # 알람이 트리거된 적이 있다고 알려준다.
              ALARM_COUNT += 1 # 알람이 한번 실행되었음을 알려준다.

              # ===============================knn모델이 졸음의 단계를 예측=======================================#

              #눈을 뜨고 있던 시간(knn모델의 y축)을 knn모델에서 사용하기 위해 test_data에 append
              test_data.append([OPENED_EYES_TIME, round(closing_time * 10, 3)])
              #눈을 뜨고 있던 시간(y) 눈을 감고 있던 시간(x)을 knn모델로 보낸다.
              result = km.run([OPENED_EYES_TIME, closing_time * 10], power, nomal, short)
              result_data.append(result) #예측결과를 result_data에 넣는다.

              # ===============================예측된 졸음의 단계에 맞는 알람을 울림=======================================#

              if not RINGING_FLAG:
                t = Thread(target=alarm.select_alarm, args=(result,))
                t.deamon = True
                t.start()
                RINGING_FLAG = True

              #===============================================================================================#
              if t.is_alive():
                RINGING_FLAG = False
                
        else: #눈을떴을때 눈을 감았을때 축적된 데이터를 초기화
          COUNTER = 0
          TIMER_FLAG = False
          RUNNING_TIME = 0
          ALARM_FLAG = False
          #==================================온습도에 따른 알림========================================#
          if SENSOR_FRAME >= 60 and RINGING_FLAG == False:
            th = Thread(target=ps.main)
            th.deamon = True
            th.start()
            SENSOR_FRAME = 0
          #============================================================================================#
          
        #=============================실시간으로 txt로 보여주는 부분================================#
        
        # 왼쪽눈 오른쪽 눈에 상자 띄워서 실시간으로 눈 종횡비 보여주는 부분
        cv2.rectangle(img, pt1=tuple(eye_rect_l[0:2]), pt2=tuple(eye_rect_l[2:4]), color=(255,255,255), thickness=1)
        cv2.rectangle(img, pt1=tuple(eye_rect_r[0:2]), pt2=tuple(eye_rect_r[2:4]), color=(255,255,255), thickness=1)
        cv2.putText(img, state_l, tuple(eye_rect_l[0:2]), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        cv2.putText(img, state_r, tuple(eye_rect_r[0:2]), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
      img = cv2.resize(img, dsize=(0, 0), fx=2.0, fy=2.0)
      winname = 'result'
      cv2.imshow(winname, img)
      cv2.moveWindow(winname, x=200, y =200)
      #========================================================================================#

      # 카메라 종료
      
    else:
      cv2.destroyAllWindows()
      
    if cv2.waitKey(1) == ord('q'):
        break
  

if __name__ == '__main__':
	main()
