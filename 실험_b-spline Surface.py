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
        
        tempIndex = interval + 1                                        # 계산식에서 인덱스를 맞추기 위해 쓰는 임시 변수
        tempCps = list(cps)                                             # 계산값 임시 저장 리스트 1
        temp = [vec2d(0, 0) for i in range(0, len(cps))]                # 계산값 임시 저장 리스트 2
        
        for k in range(1, degree + 1):              # degree 인덱스 k
            iInitial = interval - degree + k + 1    # control points 계산 결과들의 인덱스 i의 초기값 (degree마다 바뀜)
            
            for i in range(iInitial, interval + 2):                                     # i부터 최대값까지 반복 계산
                alpha = (u - knts[i - 1]) / (knts[i + degree - k] - knts[i - 1])          # 계수
                
                print("i : " + str(i) + " | iInitial : " + str(iInitial) + " | i - 1 : " + str(i - 1) + " | alpha : " + str(alpha))
                
                temp[i] = (1 - alpha) * tempCps[i - 1] + alpha * tempCps[i]         # 결과가 인덱스 (interval+1)로 모이도록 임시 저장
            
            tempCps = list(temp)        # temp에 임시저장한 계산 결과를 tempCps로 옮김
            temp = [vec2d(0, 0) for i in range(0, len(cps))]
        
        print("index : " + str(tempIndex))
        result.append([int(tempCps[tempIndex].x), int(tempCps[tempIndex].y)])
        print("result : " + str(tempCps[tempIndex].x) + ", " + str(tempCps[tempIndex].y))

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

# 해야 할 일
# 1. knot의 중복 기능 구현
# 2. numpy를 이용한 구현
# 3. b spline surface 구현