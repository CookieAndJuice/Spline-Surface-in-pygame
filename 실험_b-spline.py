import math
import numpy as np

class vec2d(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return vec2d(x, y)
    def __radd__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return vec2d(x, y)
    def __mul__(self, num):
        x = self.x * num
        y = self.y * num
        return vec2d(x, y)
    def __rmul__(self, num):
        x = self.x * num
        y = self.y * num
        return vec2d(x, y)        

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
def calB_Spline(cps, knts, degree, numJoints=30):
    
    # domain knots 계산
    start = degree - 1              # domain 시작 지점
    end = len(knts) - degree        # domain 끝 지점
    domainNum = end - start + 1     # domain knots 개수
    domainKnots = [knts[i] for i in range(start, end + 1)]
    
    # 그릴 점들 간의 간격, 그릴 점들
    h = (end - start) / numJoints
    draws = [h * a + knts[start] for a in range(0, numJoints + 1)]        # domain knots를 numJoints등분
    
    print(draws)
    
    result = []         # b spline 계산 결과
    
    # de Boor Algorithm
    for u in draws:
        if (u == knts[end]):
            interval = end - 1
        else:
            interval = findInterval(knts, u)            # knot interval 위치 찾기
            
        print("interval : " + str(interval))
        
        tempCount = 1                                                   # 계산식에서 인덱스를 맞추기 위해 쓰는 임시 변수
        tempCps = list(cps)                                             # 계산값 임시 저장 리스트 1
        temp = [vec2d(0, 0) for i in range(0, len(cps))]                # 계산값 임시 저장 리스트 2
        
        for k in range(1, degree + 1):              # degree 인덱스 k
            iInitial = interval - degree + k + 1    # control points 계산 결과들의 인덱스 i의 초기값 (degree마다 바뀜)
            
            for i in range(iInitial, interval + 2):                                     # i부터 최대값까지 반복 계산
                alpha = (u - knts[i - 1]) / (knts[interval + 1] - knts[i - 1])          # 계수
                
                print("i : " + str(i) + " | iInitial : " + str(iInitial) + " | i - tempCount : " + str(i - tempCount) + " | alpha : " + str(alpha))
                
                temp[i - tempCount] = (1 - alpha) * tempCps[i - tempCount] + alpha * tempCps[i - tempCount + 1]         # 결과가 인덱스 0으로 모이도록 임시 저장
                
            tempCount += 1
            tempCps = list(temp)        # temp에 임시저장한 계산 결과를 tempCps로 옮김
            temp = [vec2d(0, 0) for i in range(0, len(cps))]
        
        tempCount = iInitial + 1 - tempCount
        print("iInitial + 1 - tempCount : " + str(tempCount))
        result.append([int(tempCps[tempCount].x), int(tempCps[tempCount].y)])
        print("temp0 : " + str(tempCps[tempCount].x) + ", " + str(tempCps[tempCount].y))

    return result

######################################################################################

# Control Points
control_points = [vec2d(853,1080), vec2d(640,560), vec2d(1280,288), vec2d(1920,560), vec2d(1707, 1080)]

# draw_points = [vec2d(int(500 + 400 * math.cos(math.radians(theta))) / 1000, int(500 + 400 * math.sin(math.radians(theta))) / 1000) for theta in range(0, 372, 12)]

# Degree
degree = 3

# knots
knots = [i for i in range(0, len(control_points) + degree - 1)]

# for a in draw_points:
#     print("(" + str(a.x) + ", " + str(a.y) + ")")

bSplineList = calB_Spline(control_points, knots, degree)

print(bSplineList)

# 지금까지 결과
# 1. knot이 3.0일 때 x좌표가 갑자기 확 줄어든다. -> index에 문제가 있는 것이 확실하다.
# 2. 마지막에 점차 control point에 가까워지다가 마지막 결과는 control point와 동일해진다.

# 해야 할 일
# 1. knot의 중복 기능 구현
# 2. numpy를 이용한 구현
# 3. b spline surface 구현