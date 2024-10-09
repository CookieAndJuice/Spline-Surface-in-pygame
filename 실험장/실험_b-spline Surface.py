import math
import numpy as np

######################################################################################
# B Spline

# interval 찾는 함수
def findInterval(knotList, point):
    returnIndex = 0
    floorPoint = math.floor(point)
    
    for i in range(0, len(knotList)):
        
        if (floorPoint == knotList[i]):
            returnIndex = i
    
    return returnIndex

# Cubic
def calB_Spline(cps, knts, uDraws, vDraws, uIntervals, vIntervals, cpsWidth, cpsHeight, degree):
    
    uResult = []                            # u 방향 계산 결과
    result = []                             # b spline 계산 최종 결과

    # de Boor Algorithm
    
    # u 방향 계산 (계산 순서 : u 하나에 대해 모든 높이 계산 -> 다음 u 계산)
    yOffset = cpsWidth                      # 높이값 넘어갈 때 offset
    
    for drawNum in range(0, len(uDraws)):
        interval = uIntervals[drawNum]
        tempIndex = interval + 1                                           # 계산식에서 인덱스를 맞추기 위해 쓰는 임시 변수
        
        for height in range(0, cpsHeight):
            nowPos = height * yOffset
            tempCps = np.array([cps[nowPos + num] for num in range(0, cpsWidth)])       # 계산값 임시 저장 리스트
            # print("tempCps")
            # print(tempCps)
            # print("")
            
            for k in range(1, degree + 1):                                                          # degree 인덱스 k
                iInitial = interval - degree + k + 1                                                # control points 계산 결과들의 인덱스 i의 초기값 (degree마다 바뀜)
                
                for i in range(interval + 1, iInitial - 1, -1):                                             # i부터 최대값까지 반복 계산
                    alpha = (uDraws[drawNum] - knts[i - 1]) / (knts[i + degree - k] - knts[i - 1])           # 계수
                    tempCps[i] = (1 - alpha) * tempCps[i - 1] + alpha * tempCps[i]                          # 결과가 인덱스 (interval+1)로 모이도록 임시 저장
                
            uResult.append(tempCps[tempIndex])
    
    print("uResult")
    print(uResult)
    print("")
    
    # v 방향 계산
    xOffset = cpsHeight                     # 너비값 넘어갈 때 offset
    
    for drawNum in range(0, len(vDraws)):
        interval = vIntervals[drawNum]
        tempIndex = interval + 1                                           # 계산식에서 인덱스를 맞추기 위해 쓰는 임시 변수
        
        nowPos = drawNum * xOffset
        tempCps = np.array([uResult[nowPos + num] for num in range(0, cpsWidth)])       # 계산값 임시 저장 리스트
        # print("tempCps")
        # print(tempCps)
        # print("")
        
        for k in range(1, degree + 1):                                                          # degree 인덱스 k
            iInitial = interval - degree + k + 1                                                # control points 계산 결과들의 인덱스 i의 초기값 (degree마다 바뀜)
            
            for i in range(interval + 1, iInitial - 1, -1):                                             # i부터 최대값까지 반복 계산
                alpha = (vDraws[drawNum] - knts[i - 1]) / (knts[i + degree - k] - knts[i - 1])           # 계수
                tempCps[i] = (1 - alpha) * tempCps[i - 1] + alpha * tempCps[i]                          # 결과가 인덱스 (interval+1)로 모이도록 임시 저장
            
        result.append(tempCps[tempIndex])
        
    return result

######################################################################################
## screen setting ##
screenWidth = 2560
screenHeight = 1440
size = (screenWidth, screenHeight)

# B-Spline 관련 설정값들 설정하는 부분
cpsWidth = 5
cpsHeight = 5
interval = screenHeight / 5

minW = int(screenWidth / 2 - (interval * 3 / 2))
maxW = minW + interval * 3
minH = int(screenHeight / 2 - (interval * 3 / 2))
maxH = minH + interval * 3

h = interval * 3 / (cpsWidth- 1)

# Control Points
control_points = np.array([[[minW + n * h, minH + a * h] for n in range(0, cpsWidth)] for a in range(0, cpsHeight)])
for a in control_points:
    for b in a:
        print("(" + str(b[0]) + ", " + str(b[1]) + ")", end = ", ")

# Serialize Control Points
serial_cps = []
for a in control_points:
    for b in a:
        serial_cps.append(b)
serial_cps = np.array(serial_cps)
print("serial_cps")
print(serial_cps)
print("")

# serial_cpsX = []
# serial_cpsY = []

# for ax in control_points[0]:
#     serial_cpsX.append(ax.x)
# for by in control_points:
#     serial_cpsY.append(by[0].y)
# serial_cpsX = np.array(serial_cpsX)
# serial_cpsY = np.array(serial_cpsY)
# print("serial_cpsX & serial_cpsY")
# print(serial_cpsX)
# print(serial_cpsY)
# print("")

# Degree
degree = 3

# knots
knots = np.array([i for i in range(0, cpsWidth + degree - 1)])
print(knots)
print("")

# domain knots 계산
start = degree - 1              # domain 시작 지점
end = len(knots) - degree        # domain 끝 지점
domainNum = end - start + 1     # domain knots 개수

# 그릴 점 (u, v) - (start <= u, v <= end)     ## 원 -> 임의의 크기를 정해서 비율을 줄임
uDraws = np.array([int(500 + 400 * math.cos(math.radians(theta))) / 1000 * (domainNum - 1) + start for theta in range(0, 372, 12)])
vDraws = np.array([int(500 + 400 * math.sin(math.radians(theta))) / 1000 * (domainNum - 1) + start for theta in range(0, 372, 12)])
print("uDraws & vDraws")
print(uDraws)
print(vDraws)
print("")

# interval lists        
uIntervals = []
for ud in range(0, len(uDraws)):
    interval = 0
    if (uDraws[ud] == knots[end]):
        interval = end - 1
    else:
        interval = findInterval(knots, uDraws[ud])
    uIntervals.append(interval)

vIntervals = []
for vd in range(0, len(vDraws)):
    interval = 0
    if (vDraws[vd] == knots[end]):
        interval = end - 1
    else:
        interval = findInterval(knots, vDraws[vd])
    vIntervals.append(interval)

uIntervals = np.array(uIntervals)
vIntervals = np.array(vIntervals)

######################################################################################

print("B-Spline 결과")
bSplineList = calB_Spline(serial_cps, knots, uDraws, vDraws, uIntervals, vIntervals, cpsWidth, cpsHeight, degree)
print(bSplineList)
print(bSplineList[0].dtype)
print("")

# 완전히 잘못 생각해서, control points가 무조건 5x5 정사각형일 거라고 가정하고 코드를 짰다.
# 이를 바로잡기 위해
# 첫번째 생각대로 코드를 다시 짜려 한다.
# 동일한 함수에 width와 height를 반대로 넣고, wOffset과 hOffset을 반대로 넣으면 u 방향과 v 방향을 둘 다 만들 수 있게 할 것이다.

# 이번에 잘못 생각한 점
# 어차피 B-Spline Surface는 u 방향 -> v 방향 혹은 그 반대 순서로 파이프라인이 되어 있으므로 분리가 불가능하다.
# 그러니 그냥 하나의 함수에 연속으로 넣는 것이 더 낫다.