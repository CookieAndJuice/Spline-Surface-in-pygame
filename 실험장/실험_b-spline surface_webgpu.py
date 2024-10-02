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
def calB_Spline(cps, knts, degree, uDraws, vDraws, uIntervals, vIntervals):
    
    # domain knots 계산
    end = len(knts) - degree        # domain 끝 지점
    
    uResult = [[] for a in range(0, len(cps))]      # u 방향 b spline 계산 결과
    print(uResult)
    print("\n")
    result = []                     # b spline 계산 최종 결과
    
    # de Boor Algorithm
    # for u in range(0, len(uDraws)):
    #     uInterval = uIntervals[u]
    #     for v in range(0, len(vDraws)):
    #         vInterval = vIntervals[v]
    #         uTempIndex = uInterval + 1                                  # 계산식에서 인덱스를 맞추기 위해 쓰는 임시 변수1
    #         vTempIndex = vInterval + 1                                  # 계산식에서 인덱스를 맞추기 위해 쓰는 임시 변수2

    #         tempCps = [arr[:] for arr in cps]                           # 계산값 임시 저장 리스트 1

    #         for height in range(0, len(tempCps)):
    #             temp = [vec2d(0, 0) for i in range(0, len(cps))]            # 계산값 임시 저장 리스트 2
            
    #             for k in range(1, degree + 1):              # degree 인덱스 k
    #                 iInitial = interval - degree + k + 1    # control points 계산 결과들의 인덱스 i의 초기값 (degree마다 바뀜)
                    
    #                 for i in range(iInitial, interval + 2):                                     # i부터 최대값까지 반복 계산
    #                     alpha = (uDraws[u] - knts[i - 1]) / (knts[i + degree - k] - knts[i - 1])        # 계수
                        
    #                     temp[i] = (1 - alpha) * tempCps[height][i - 1] + alpha * tempCps[height][i]         # 결과가 인덱스 (interval+1)로 모이도록 임시 저장
                    
    #                 tempCps[height] = list(temp)        # temp에 임시저장한 계산 결과를 tempCps로 옮김
    #                 temp = [vec2d(0, 0) for i in range(0, len(cps))]
                
    #             uResult[height].append(tempCps[height][tempIndex])


    # 예전 de Boor Algorithm
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

    for v in range(0, len(vDraws)):         # v 방향 b spline
        interval = vIntervals[v]
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
## screen setting ##
screenWidth = 2560
screenHeight = 1440
size = (screenWidth, screenHeight)

# B-Spline 관련 설정값들 설정하는 부분
cpsNum = 5
cpsLen = cpsNum * cpsNum
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
knots = np.array([i for i in range(0, cpsNum + degree - 1)])
print(knots)

# Serialize Control Points
serial_cps = []
for points in control_points:
    for point in points:
        serial_cps.append(point.x)
        serial_cps.append(point.y)
serial_cps = np.array(serial_cps)

# domain knots 계산
start = degree - 1              # domain 시작 지점
end = len(knots) - degree        # domain 끝 지점
domainNum = end - start + 1     # domain knots 개수

# 그릴 점 (u, v) - (start <= u, v <= end)     ## 원 -> 임의의 크기를 정해서 비율을 줄임
uDraws = np.array([int(500 + 400 * math.cos(math.radians(theta))) / 1000 * (domainNum - 1) + start for theta in range(0, 372, 12)])
vDraws = np.array([int(500 + 400 * math.sin(math.radians(theta))) / 1000 * (domainNum - 1) + start for theta in range(0, 372, 12)])
print(uDraws)
print(vDraws)

# interval lists
uIntervals = []
for u in uDraws:
    interval = 0
    if (u == knots[end]):
        interval = end - 1
    else:
        interval = findInterval(knots, u)
    uIntervals.append(interval)
uIntervals = np.array(uIntervals)

vIntervals = []
for v in vDraws:
    interval = 0
    if (v == knots[end]):
        interval = end - 1
    else:
        interval = findInterval(knots, v)
    vIntervals.append(interval)
vIntervals = np.array(vIntervals)

######################################################################################
# B Spline Function

compute_B_Spline_code = """
@group(0) @binding(0)
var<storage, read> uInputs: array<f32>;

@group(0) @binding(1)
var<storage, read> vInputs: array<f32>;

@group(0) @binding(2)
var<storage, read> cps: array<f32>;

@group(0) @binding(3)
var<storage, read> knots: array<u32>;

@group(0) @binding(4)
var<storage, read> uIntervals: array<u32>;

@group(0) @binding(5)
var<storage, read> vIntervals: array<u32>;

@group(0) @binding(6)
var<storage, read_write> output: array<u32>;

@compute @workgroup_size(32)
fn main(@builtin(global_invocation_id) global_invocation_id: vec3u)
{
    let degree = u32(%d);
    let cpsWidth = u32(%d);
    let cpsHeight = u32(%d);
    var uResult: array<vec2<f32>, %d>;

    // u 방향 b spline
    let uInterval = uIntervals[global_invocation_id.x];
    var uTempIndex = uInterval + 1;

    let cpsNum = u32(%d);
    var tempCps: array<vec2<f32>, %d>;

    var index = 0u;
    while(index < cpsNum * 2)
    {
        tempCps[index].x = cps[index];
        tempCps[index].y = cps[index + 1];
        index += 2u;
    }

    var height = 0u;
    while (height * cpsWidth < cpsNum)
    {
        var tempArr: array<vec2<f32>, %d>;

        for (var k = 1u; k < degree + 1; k++)
        {
            var a = 0u;
            while (a < cpsNum)
            {
                tempArr[a] = vec2<f32>(0.0, 0.0);
                a += 2u;
            }

            var iInitial = uInterval - degree + k + 1;

            for (var i = iInitial; i < uInterval + 2; i++)
            {
                let alpha = (uInputs[global_invocation_id.x] - f32(knots[i - 1])) / f32(knots[i + degree - k] - knots[i - 1]);

                tempArr[i] = (1 - alpha) * tempCps[i - 1 + height * cpsWidth] + alpha * tempCps[i + height * cpsWidth];
            }

            for (var i = 0u; i < cpsWidth; i++)
            {
                tempCps[i + height * cpsWidth] = tempArr[i];
            }
        }
        uResult[height] = tempCps[uTempIndex + height * cpsWidth];
        height++;
    }
    
    // v 방향 b spline
    let vInterval = vIntervals[global_invocation_id.x];
    var vTempIndex = vInterval + 1;
    
}

""" % (degree, cpsNum, cpsNum, cpsNum, cpsLen, cpsLen, cpsLen)

out = np.zeros(len(serial_cps), dtype=np.uint32)
out = compute_with_buffers({0: uDraws, 1: vDraws, 2: serial_cps, 3: knots, 4: uIntervals, 5: vIntervals},
                           {6: out.nbytes}, compute_B_Spline_code, n = 32)
# Select data from buffer at binding 4
bSplines = np.frombuffer(out[6], dtype=np.uint32)
print(bSplines.tolist())
print(len(bSplines))

######################################################################################

bSplineList = calB_Spline(control_points, knots, degree, uDraws, vDraws, uIntervals, vIntervals)

print(bSplineList)

## vec2d 형태를 1차원 배열 형태로 직렬화해서 셰이더에 넘겨야 한다.
## 그 말은 출력할 때에도 반대로 해줘야 해야한다는 소리
## compute shader에서 어떤 것을 병렬처리로 계산해야 할 지 정해야 함 -> 아마 u방향, v방향 knot들에 대한 de boor 알고리즘일 듯
