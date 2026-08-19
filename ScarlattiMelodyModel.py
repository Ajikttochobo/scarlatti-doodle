import torch
import torch.nn as nn
import partitura as pt
import numpy as np
import torch

# 0. 맥북 장치 설정 (Apple Silicon GPU 가속)
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu") # metal performance shaders 사용할 수 있으면 사용하고 못하면 걍 cpu 사용

# 1. UNet 블록 및 모델 정의
class DoubleConv(nn.Module): # doubleconv를 따로 클래스로 만들어 두는 이유는 이게 모델에서 여러번 쓰이기 때문!!
    def __init__(self, in_channels, out_channels):  # __init__은 클래스로부터 객체를 만들 때 자동으로 실행되는 초기화 함수(생성자)!!! 첫번째 인자는 지금 만들어지는 함수이고 나머지 인자들로 객체에 넣을 데이터 지정!
        super().__init__() # 부모 클래스의 객체를 반환 (상위 클래스의 초기화 함수를 자식 클래스에서 그대로 쓸 수 있게 해줌) 자식 클래스에서 부모 클래스의 초기화 함수를 그대로 실행
        self.conv = nn.Sequential( # nn.Sequential은 여러 신경망 층(layer)을 순서대로 감싸는 순차 컨테이너 모듈, 처리 과정을 뭉쳐서 변수에 담을 수 있게 만듦 레이어가 가진 가중치를 계속 저장하기 위에 변수에 저장
            # 변수 선언 시 앞에 self. 붙이는 이유는 안붙이면 init 함수가 끝나면 바로 사라지기 때문
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1), # 여기서 쓰인 인자는 인풋, 아웃풋, 커널 사이즈(필터의 크기, 여기서는 3이므로 3 x 3 필터),  입력 이미지 테두리에 추가할 0 등의 픽셀 수인 padding (출력 크기 감소 방지, 테두리 정보 보호, 모델을 더 깊게 만들기 위해)
            nn.BatchNorm2d(out_channels), # 데이터가 너무 크거나 작아지지 않도록 평균을 1 분산을 0으로 해서 고르게 펴줌
            nn.ReLU(inplace=True), # 활성화함수 (inplace=True 는 연산 결과를 새로운 메모리에 저장하지 않고, 입력받은 원본 텐서의 데이터를 직접 덮어쓰기하겠다는 뜻)
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x): # 파이토치 모듈에서 순전파를 자동으로 실행하게 되어 있어서 순전파 함수를 만들어주어야 함
        return self.conv(x)

class MelodyUNet(nn.Module):
    def __init__(self, in_channels=1, num_classes=3): # 여기서 num_classes는 음 시작은 2 지속은 1 없는거는 0 구분용 그래서 채널이 3개가 나오는거
        super().__init__()

        self.inc = DoubleConv(in_channels, 32) # 위에서 만든 변수를 inc(input convolution, 모델에서 처음으로 거치는 블록) 변수에 할당
        self.pool1 = nn.MaxPool2d(2) # 커널 사이즈를 2로 지정해서 풀링층을 통과

        self.down1 = DoubleConv(32, 64)
        self.pool2 = nn.MaxPool2d(2)

        self.bottleneck = DoubleConv(64, 128)

        self.up2 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2) # 일반 컨볼루션의 반대로 진행되는 전치 합성곱(Transposed Convolution)을 진행, 인자는 인풋 아웃풋 커널 사이즈와 필터가 이동하는 간격인 stride(여기서는 stride 가 2기 때문에 이미지가 2배 커짐)
        self.dec2 = DoubleConv(128, 64)

        self.up1 = nn.ConvTranspose2d(64, 32, kernel_size=2, stride=2)
        self.dec1 = DoubleConv(64, 32)

        self.outc = nn.Conv2d(32, num_classes, kernel_size=1) # outc 는 out convolution이라는 뜻!! 커널 크기를 1로 해서 특징만 요약!!

    def forward(self, x):
        # ********인코더********
        x1 = self.inc(x) # input convolution 변수에 인풋값(x) 집어넣어서 할당
        x2 = self.down1(self.pool1(x1)) # 인코더(풀링층1(x1)) 구조
        
        x_bottleneck = self.bottleneck(self.pool2(x2)) # doubleconv(풀링층2(x2)) 구조

        #********디코더********
        x = self.up2(x_bottleneck) # transposed convolution에 x_bottleneck 넣어서 실행
        x = torch.cat([x, x2], dim=1) # 두 텐서를 1번 차원(dim) 즉 열 방향으로 이어붙임 (cat은 concatenate의 약자)
        x = self.dec2(x) # x를 doubleconv에 대입

        x = self.up1(x)
        x = torch.cat([x, x1], dim=1)
        x = self.dec1(x)

        logits = self.outc(x) # logits이란 모델의 마지막 층에서 활성화 함수(시그모이드나 소프트맥스 등)를 거치기 전 상태인 원시 점수(raw score)
        return logits

# ********scoreToDataset, datasetToScore 함수********
def ScoreToDataset(partituraPerformance : pt.performance.PerformedPart):
    '''스코어 파일을 ai 학습용 데이터셋으로 변환해서 리턴'''
    array = np.zeros((128, 40 * 30))
    note_array = partituraPerformance.note_array().copy()

    for i in range(len(note_array)):
        pitch = note_array[i]['pitch']
        startPoint = int(round(note_array[i]['onset_sec'] * 1000 / 25))
        endPoint = int(round((note_array[i]['onset_sec'] + note_array[i]['duration_sec']) * 1000 / 25))

        if(startPoint >= 1200):
            continue
        endPoint = min(endPoint, 1200)

        array[pitch, startPoint] = 2 # 음이 시작하는 부분은 2로 설정해서 표시
        startPoint += 1

        if(startPoint < endPoint):
            array[pitch, startPoint:endPoint] = 1

    return array

def DatasetToScore(dataset : np.ndarray):
    '''ai가 출력한 데이터셋을 스코어 파일로 변환해서 리턴'''
    note_list = []

    indices = np.where(dataset == 2)
    coordinates = list(zip(indices[0], indices[1])) # 음이 시작하는 위기들 모두 찾기
    for coordinate in coordinates:
        coordinatePitch, coordinateStartPoint = coordinate
        endPoint = 1
        while(coordinateStartPoint + endPoint < 1200 and dataset[coordinatePitch][coordinateStartPoint + endPoint] == 1):
            endPoint += 1
        
        # 반복문 돌면서 복원한 값 집어넣기
        note_list.append((
            coordinateStartPoint / 40.0,
            endPoint / 40.0,
            int(coordinatePitch),
            127
        ))
    
    fields = [('onset_sec', 'f8'), ('duration_sec', 'f8'), ('pitch', 'i4'), ('velocity', 'i4')]
    note_array = np.array(note_list, dtype=fields)

    return pt.performance.PerformedPart.from_note_array(note_array)

# ********모델 실행 코드********
def runModel(inputMidi):
    test_performance = pt.load_performance_midi(inputMidi) # 미디 파일 불러와서 partitura performance로 변환

    input_data = ScoreToDataset(test_performance) # 넘파이 어레이로 변환
    input_tensor = torch.from_numpy(input_data).float() # 4d 텐서로 변환

    # 배치(1)와 채널(1) 차원 추가 (4차원으로 만듦)
    if input_tensor.ndim == 2:  # 2차원일때([128, 1200] 인 경우)
        input_tensor = input_tensor.unsqueeze(0).unsqueeze(0)  # [1, 1, 128, 1200]
    elif input_tensor.ndim == 3:  # 3차원일때([1, 128, 1200] 인 경우)
        input_tensor = input_tensor.unsqueeze(0)

    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu") #디바이스 설정
    model = MelodyUNet(in_channels=1, num_classes=3).to(device) # 만들어둔 모델 불러옴

    checkpoint = torch.load("melody_unet_checkpoint.pth", map_location=device) # 딥러닝 모델 파일 불러옴 (map_location은 모델이 저장되었을때의 장치와 지금 실행하는 컴퓨터의 장치가 달라도 에러 없이 지정한 장치로 매핑하여 불러올 수 있게 하는거)
    model.load_state_dict(checkpoint) # 미리 저장해둔 가중치와 평향을 모델 객체에 덮어씌워 모델의 상태를 복원

    model.eval() # 평가 모드

    input_tensor = input_tensor.to(device) # 입력 텐서도 모델과 같은 디바이스로 이동

    with torch.no_grad():
        logits = model(input_tensor)
        probs = torch.sigmoid(logits)

    probs_matrix = probs.squeeze(0).cpu().numpy()

    # 음 시작, 음 지속 기준을 다르게 할 수 있음
    ONSET_THRESHOLD = 0.375   # 음 시작
    SUSTAIN_THRESHOLD = 0.375 # 음 지속 TODO 이거 고쳐도 반영이 왜 안되지??? (반영 되는지 안되는지 모르겠다...)

    onset_mask = probs_matrix[1] > ONSET_THRESHOLD
    sustain_mask = probs_matrix[2] > SUSTAIN_THRESHOLD # 불리언 마스킹

    result_matrix = np.zeros_like(probs_matrix[0], dtype=np.int64) # probs_matrix[0] 모양으로 영행렬 만듦
    result_matrix[sustain_mask] = 2
    result_matrix[onset_mask] = 1 # 만들어두었던 불리언 마스크로 숫자 지정

    result_performance = DatasetToScore(result_matrix)
    pt.save_performance_midi(result_performance, "output_performance.mid") # 미디파일로 저장

    return "output_performance.mid"