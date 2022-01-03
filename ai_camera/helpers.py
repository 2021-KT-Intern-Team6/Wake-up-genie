# file_name: helpers.py
# file_function: csv파일을 읽어와서 다시 이미지 형식과 정답 tag로 분류

#========= Import library ===========#
import numpy as np
import csv
#===================================#

# function_name: read_csv
# input: path(csv파일 경로)
# output: imgs, tgs (csv파일안에 있는 데이터의 이미지, 정답 tag)
# function: csv파일을 읽어와서 다시 이미지 형식과 정답 tag로 분류해주는 함수

def read_csv(path):
  #이미지 크기 지정
  width = 34
  height = 26
  dims = 1

  with open(path,'r') as f:
    #디렉토리 포멧으로 csv파일을 읽어오기
    reader = csv.DictReader(f)
    rows = list(reader)

  #imgs: 모든 이미지가 포함된 numpy 배열
  #tgs: 이미지 태그가 있는 numpy 배열
  imgs = np.empty((len(list(rows)),height,width, dims),dtype=np.uint8)
  tgs = np.empty((len(list(rows)),1))

  #목록을 이미지 형식으로 다시 변환
  for row,i in zip(rows,range(len(rows))):
    img = row['image']
    img = img.strip('[').strip(']').split(', ')
    im = np.array(img, dtype=np.uint8)
    im = im.reshape((height, width))
    im = np.expand_dims(im, axis=2)
    imgs[i] = im

    #'open'=1 / 'close'=0으로 tag설정
    tag = row['state']
    if tag == 'open':
      tgs[i] = 1
    else:
      tgs[i] = 0

  #shuffle the dataset
  index = np.random.permutation(imgs.shape[0])
  imgs = imgs[index]
  tgs = tgs[index]

  #이미지 및 해당 태그 반환
  return imgs, tgs