# knn 알고리즘을 학습시켜 졸음의 단계를 분류
# 졸음의 단계를 사고를 예방할 수있는 시간을 기준으로 3단계로 나누고
# cnn 모델로 측정한 눈을 감고있는 시간을 knn알고리즘을 통해 가까운 k개의 이웃 중 가장 흔한 단계(label)로 분류

import numpy as np
import cv2
import matplotlib.pyplot as plt
from sklearn import metrics

# %matplotlib inline
# plt.style.use('ggplot')


knn = cv2.ml.KNearest_create()                                  # knn 알고리즘 객체 생성


# 랜덤하게 많은 data point 생성
# 'num_samples' : 생성할 data point의 갯수
# 'num_features' : 각 data point의 feature 갯수
def generate_data(num_samples, num_features=2):
    data_size = (num_samples, num_features)
    data = np.random.randint(0, 40, size=data_size)
    return data.astype(np.float32)


# 사고를 예방할 수 있는 시간을 기준으로 졸음 운전 위험도(label)를 결정
# 30FPS 카메라를 기준으로 100km/h로 달리는 차가 100m 이상 차간 거리를 유지하고 있는 경우
# 사람의 반응 시간과 브레이크를 밟는데 걸리는 시간, 제동하는데 걸리는 시간을 고려해 1초정도의 시간이 걸린다고 가정
# x : 눈을 뜨고 있던 시간(s), y : 눈을 감고 있는 시간(s)
# y = x/2 + 15와 y = x - 15로 단계 구분 (단계가 높을수록 졸음 정도가 낮음)
def classify_label(train_data):
    labels = []
    for data in train_data:
        if data[1] < data[0] - 15:
            labels.append(2)
        elif data[1] >= (data[0] / 2 + 15):
            labels.append(0)
        else:
            labels.append(1)
    return np.array(labels)


# label별로 난수 배열을 나눔
def binding_label(train_data, labels):
    power = train_data[labels == 0]
    nomal = train_data[labels == 1]
    short = train_data[labels == 2]
    return power, nomal, short

# knn 알고리즘 학습 시작을 위한 함수, input data의 size를 parameter로 받음
def start(sample_size=25):
    train_data = generate_data(sample_size)
    # print("train_data :",train_data)
    labels = classify_label(train_data)
    power, nomal, short = binding_label(train_data, labels)
    print("Return true if training is successful :", knn.train(train_data, cv2.ml.ROW_SAMPLE, labels))  # data와 label을 전달해 모델을 학습
    return power, nomal, short


# 학습한 knn 알고리즘에 따라 새로운 data의 label을 예측(분류)
def run(new_data, power, nomal, short):
    a = np.array([new_data])
    b = a.astype(np.float32)
    # plot_data(power, nomal, short)
    ret, results, neighbor, dist = knn.findNearest(b, 5)  # k 값을 5로 주어 가장 가짜운 5개의 값중 가장 흔한 값으로 label 설정하도록 함
    # print("Neighbor's label : ", neighbor)
    print("predicted label : ", results)
    # print("distance to neighbor : ", dist)
    # print("what is this : ", ret)
    # plt.plot(b[0,0], b[0,1], 'm*', markersize=14);
    return int(results[0][0])                             # 각 input data에 대한 예측 결과를 return


def plot_data(po, no, sh):
    plt.figure(figsize=(10, 6))
    plt.scatter(po[:, 0], po[:, 1], c='r', marker='s', s=50)
    plt.scatter(no[:, 0], no[:, 1], c='g', marker='^', s=50)
    plt.scatter(sh[:, 0], sh[:, 1], c='b', marker='o', s=50)
    plt.xlabel('x is second for alarm term')
    plt.ylabel('y is 10s for time to close eyes')


# knn 알고리즘의 정확도 평가
# def accuracy_score(acc_score, test_score):
#     """Function for Accuracy Calculation"""
#     print("KNN Accuracy :", np.sum(acc_score == test_score) / len(acc_score))
    # A line below this comment is exactly same with above one.
    # print(metrics.accuracy_score(acc_score, test_score))

# knn 알고리즘의 정밀도 평가 (ex. 모델이 1이라고 예측한 것 중 실제로 1인것)
# def precision_score(acc_score, test_score):
#     """Function for Precision Calculation"""
#     true_two = np.sum((acc_score == 2) * (test_score == 2))
#     false_two = np.sum((acc_score != 2) * (test_score == 2))
#     precision_two = true_two / (true_two + false_two)
#     print("Precision for the label '2' :", precision_two)
#
#     true_one = np.sum((acc_score == 1) * (test_score == 1))
#     false_one = np.sum((acc_score != 1) * (test_score == 1))
#     precision_one = true_one / (true_one + false_one)
#     print("Precision for the label '1' :", precision_one)
#
#     true_zero = np.sum((acc_score == 0) * (test_score == 0))
#     false_zero = np.sum((acc_score != 0) * (test_score == 0))
#     precision_zero = true_zero / (true_zero + false_zero)
#     print("Precision for the label '0' :", precision_zero)