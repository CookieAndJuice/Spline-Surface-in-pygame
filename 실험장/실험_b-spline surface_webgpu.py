import math
import numpy as np
from wgpu.utils.compute import compute_with_buffers

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
    print(domainKnots)

    # 그릴 점 (u, v) - (start <= u, v <= end)     ## 원 -> 임의의 크기를 정해서 비율을 줄임
    uDraws = [int(500 + 400 * math.cos(math.radians(theta))) / 1000 * (domainNum - 1) + start for theta in range(0, 372, 12)]
    vDraws = [int(500 + 400 * math.sin(math.radians(theta))) / 1000 * (domainNum - 1) + start for theta in range(0, 372, 12)]
    print(uDraws)
    print(vDraws)
    
    uResult = [[] for a in range(0, len(cps))]      # u 방향 b spline 계산 결과
    print(uResult)
    result = []                     # b spline 계산 최종 결과
    
    # de Boor Algorithm
    for u in uDraws:         # u 방향 b spline
        if (u == knts[end]):
            interval = end - 1
        else:
            interval = findInterval(knts, u)            # knot interval 위치 찾기
        
        tempIndex = interval + 1                                        # 계산식에서 인덱스를 맞추기 위해 쓰는 임시 변수
        tempCps = [arr[:] for arr in cps]                               # 계산값 임시 저장 리스트 1

        for height in range(0, len(tempCps)):
            temp = [vec2d(0, 0) for i in range(0, len(cps))]            # 계산값 임시 저장 리스트 2
        
            for k in range(1, degree + 1):              # degree 인덱스 k
                iInitial = interval - degree + k + 1    # control points 계산 결과들의 인덱스 i의 초기값 (degree마다 바뀜)
                
                for i in range(iInitial, interval + 2):                                     # i부터 최대값까지 반복 계산
                    alpha = (u - knts[i - 1]) / (knts[i + degree - k] - knts[i - 1])        # 계수
                    
                    temp[i] = (1 - alpha) * tempCps[height][i - 1] + alpha * tempCps[height][i]         # 결과가 인덱스 (interval+1)로 모이도록 임시 저장
                
                tempCps[height] = list(temp)        # temp에 임시저장한 계산 결과를 tempCps로 옮김
                temp = [vec2d(0, 0) for i in range(0, len(cps))]
            
            uResult[height].append(tempCps[height][tempIndex])

    # 지금 u 방향으로 만든 모든 점들을 v 방향으로 모조리 알고리즘을 통해 점으로 만들기 때문에 무조건 정사각형 모양이 된다.
    # 따라서 원을 그리려면 알고리즘을 u마다 v 하나만 나오도록(bezier surface처럼) 수정해야 한다.
    # 근데 그렇게 하면 범용성이 떨어지지 않을까??
    for v in range(0, len(vDraws)):         # v 방향 b spline
        if (vDraws[v] == knts[end]):
            interval = end - 1
        else:
            interval = findInterval(knts, vDraws[v])            # knot interval 위치 찾기

        tempIndex = interval + 1                                        # 계산식에서 인덱스를 맞추기 위해 쓰는 임시 변수
        tempCps = [arr[:] for arr in uResult]                           # 계산값 임시 저장 리스트 1

        temp = [vec2d(0, 0) for i in range(0, len(uResult))]            # 계산값 임시 저장 리스트 2

        for k in range(1, degree + 1):              # degree 인덱스 k
            iInitial = interval - degree + k + 1    # control points 계산 결과들의 인덱스 i의 초기값 (degree마다 바뀜)
            
            for i in range(iInitial, interval + 2):                                     # i부터 최대값까지 반복 계산
                alpha = (vDraws[v] - knts[i - 1]) / (knts[i + degree - k] - knts[i - 1])        # 계수
                
                temp[i] = (1 - alpha) * tempCps[i - 1][v] + alpha * tempCps[i][v]         # 결과가 인덱스 (interval+1)로 모이도록 임시 저장
            
            for num in range(0, len(temp)):
                tempCps[num][v] = temp[num]        # temp에 임시저장한 계산 결과를 tempCps로 옮김
            temp = [vec2d(0, 0) for i in range(0, len(uResult))]
        
        result.append([int(tempCps[tempIndex][v].x), int(tempCps[tempIndex][v].y)])

    return result

######################################################################################
# Compute Shader Code

uDrs = [int(500 + 400 * math.cos(math.radians(theta))) / 1000 * (domainNum - 1) + start for theta in range(0, 372, 12)]

compute_shader_code = """

@group(0) @binding(0)
var<storage, read> input: array<f32>;

@group(0) @binding(1)
var<storage, read_write> output: array<f32>;

const nums = 372 / 12;

@compute @workgroup_size(1)
fn ComputeFunc(@builtin()) {
    
}

"""

######################################################################################

## screen setting ##
screenWidth = 2560
screenHeight = 1440
size = (screenWidth, screenHeight)

# B-Spline 관련 설정값들 설정하는 부분
cpsNum = 5
interval = screenHeight / 5

minW = int(screenWidth / 2 - (interval * 3 / 2))
maxW = minW + interval * 3
minH = int(screenHeight / 2 - (interval * 3 / 2))
maxH = minH + interval * 3

h = interval * 3 / (cpsNum- 1)

# Control Points
control_points = [[vec2d(minW + n * h, minH + a * h) for n in range(0, cpsNum)] for a in range(0, cpsNum)]
for a in control_points:
    for b in a:
        print("(" + str(b.x) + ", " + str(b.y) + ")", end = ", ")

# Degree
degree = 3

# knots
knots = [i for i in range(0, cpsNum + degree - 1)]
print(knots)

# for a in draw_points:
#     print("(" + str(a.x) + ", " + str(a.y) + ")")

bSplineList = calB_Spline(control_points, knots, degree)

print(bSplineList)