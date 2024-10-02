import math
import numpy as np
from wgpu.utils.compute import compute_with_buffers

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
def calB_Spline(cps, cpsWidth, knts, degree, draws, intervals):
    
    end = len(knts) - degree        # domain knots 끝 지점    
    result = []                     # b spline 계산 최종 결과
    cpsHeight = len(cps) / cpsWidth

    # de Boor Algorithm
    height = 0
    for d in range(0, len(draws)):
        while(height < cpsHeight):
            wOffset = height * cpsWidth
            
            interval = intervals[d]
            height += 1



    for u in range(0, len(uDraws)):         # u 방향 b spline
        interval = uIntervals[u]
        tempIndex = interval + 1                                        # 계산식에서 인덱스를 맞추기 위해 쓰는 임시 변수
        tempCps = [arr[:] for arr in cps]                               # 계산값 임시 저장 리스트 1

        for height in range(0, len(tempCps)):
            temp = [vec2d(0, 0) for i in range(0, len(cps))]            # 계산값 임시 저장 리스트 2
        
            for k in range(1, degree + 1):              # degree 인덱스 k
                iInitial = interval - degree + k + 1    # control points 계산 결과들의 인덱스 i의 초기값 (degree마다 바뀜)
                
                for i in range(iInitial, interval + 2):                                     # i부터 최대값까지 반복 계산
                    alpha = (uDraws[u] - knts[i - 1]) / (knts[i + degree - k] - knts[i - 1])        # 계수
                    
                    temp[i] = (1 - alpha) * tempCps[height][i - 1] + alpha * tempCps[height][i]         # 결과가 인덱스 (interval+1)로 모이도록 임시 저장
                
                tempCps[height] = list(temp)        # temp에 임시저장한 계산 결과를 tempCps로 옮김
                temp = [vec2d(0, 0) for i in range(0, len(cps))]
            
            uResult[height].append(tempCps[height][tempIndex])

    for a in uResult:
        print(len(a))
        for b in a:
            print("(" + str(b.x) + ", " + str(b.y) + ")", end = ", ")
        print("\n")
    print(len(uResult))

    return result

######################################################################################
## screen setting ##
screenWidth = 2560
screenHeight = 1440
size = (screenWidth, screenHeight)

# B-Spline 관련 설정값들 설정하는 부분
cpsWidth = 5
cpsHeight = 5
cpsLen = cpsWidth * cpsHeight
interval = screenHeight / 5

minW = int(screenWidth / 2 - (interval * 3 / 2))
maxW = minW + interval * 3
minH = int(screenHeight / 2 - (interval * 3 / 2))
maxH = minH + interval * 3

h = interval * 3 / (cpsWidth- 1)

# Control Points
# control_points = np.array([[[minW + n * h, minH + a * h] for n in range(0, cpsWidth)] for a in range(0, cpsHeight)])
# for a in control_points:
#     for b in a:
#         print("(" + str(b[0]) + ", " + str(b[1]) + ")", end = ", ")

# Serialize Control Points
serial_cps = []
for a in range(0, cpsHeight):
    for b in range(0, cpsWidth):
        serial_cps.append([minW + b * h, minH + a * h])
serial_cps = np.array(serial_cps)

# Degree
degree = 3

# knots
knots = np.array([i for i in range(0, cpsWidth + degree - 1)])
print(knots)

# domain knots 계산
start = degree - 1              # domain 시작 지점
end = len(knots) - degree        # domain 끝 지점
domainNum = end - start + 1     # domain knots 개수

# 그릴 점 (u, v) - (start <= u, v <= end)     ## 원 -> 임의의 크기를 정해서 비율을 줄임
uDraws = np.array([int(500 + 400 * math.cos(math.radians(theta))) / 1000 * (domainNum - 1) + start for theta in range(0, 372, 12)])
vDraws = np.array([int(500 + 400 * math.sin(math.radians(theta))) / 1000 * (domainNum - 1) + start for theta in range(0, 372, 12)])

# interval lists
intervals = []
for d in range(0, len(uDraws)):
    uInterval = 0
    vInterval = 0

    if (d[0] == knots[end]):
        uInterval = end - 1
    else:
        uInterval = findInterval(knots, d[0])

    if (d[1] == knots[end]):
        vInterval = end - 1
    else:
        vInterval = findInterval(knots, d[1])
    intervals.append([uInterval, vInterval])
        
intervals = np.array(intervals)

######################################################################################

# # u방향 b spline 적용
# uBSplineList = calB_Spline(control_points, cpsWidth, knots, degree, draws, intervals)
# print(uBSplineList)
# np.transpose(uBSplineList)

# # v방향 b spline 적용
# finalBSplineList = calB_Spline(uBSplineList, cpsHeight, knots, degree, draws, intervals)
# print(finalBSplineList)