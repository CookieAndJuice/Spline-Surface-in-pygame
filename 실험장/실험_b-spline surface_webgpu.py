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
def calB_Spline(cps, knts, degree, uDraws, vDraws):
    
    # domain knots 계산
    end = len(knts) - degree        # domain 끝 지점

    # 그릴 점 (u, v) - (start <= u, v <= end)     ## 원 -> 임의의 크기를 정해서 비율을 줄임
    # uDraws = [int(500 + 400 * math.cos(math.radians(theta))) / 1000 * (domainNum - 1) + start for theta in range(0, 372, 12)]
    # vDraws = [int(500 + 400 * math.sin(math.radians(theta))) / 1000 * (domainNum - 1) + start for theta in range(0, 372, 12)]
    # print(uDraws)
    # print(vDraws)
    
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

# Serialize Control Points
serial_cps = []
for points in control_points:
    for point in points:
        serial_cps.append(point.x)
        serial_cps.append(point.y)

######################################################################################
# Compute Shader Code

# domain knots 계산
start = degree - 1              # domain 시작 지점
end = len(knots) - degree        # domain 끝 지점
domainNum = end - start + 1     # domain knots 개수

uDrs = [(500 + 400 * math.cos(math.radians(theta))) / 1000 * (domainNum - 1) + start for theta in range(0, 372, 12)]
print("uDrs")
print(uDrs)

compute_uDraws_code = """

@group(0) @binding(0)
var<storage, read> input: array<u32>;

@group(0) @binding(1)
var<storage, read_write> output: array<f32>;

@compute @workgroup_size(32)
fn main(@builtin(workgroup_id) workgroup_id : vec3<u32>,
      @builtin(local_invocation_id) local_invocation_id : vec3<u32>,
      @builtin(global_invocation_id) global_invocation_id : vec3<u32>,
      @builtin(local_invocation_index) local_invocation_index: u32,
      @builtin(num_workgroups) num_workgroups: vec3<u32>
    ) {
    let workgroup_index =  
       workgroup_id.x +
       workgroup_id.y * num_workgroups.x +
       workgroup_id.z * num_workgroups.x * num_workgroups.y;

    let global_invocation_index =
       workgroup_index * 32 +
       local_invocation_index;
    
    let theta = f32(input[global_invocation_index]);

    var draw = (500 + 400 * cos(radians(theta)));
    draw = draw / 1000 * (%d - 1) + %d;

    output[global_invocation_index] = draw;
}

""" % (domainNum, start)

compute_vDraws_code = """

@group(0) @binding(0)
var<storage, read> input: array<u32>;

@group(0) @binding(1)
var<storage, read_write> output: array<f32>;

@compute @workgroup_size(32)
fn main(@builtin(workgroup_id) workgroup_id : vec3<u32>,
      @builtin(local_invocation_id) local_invocation_id : vec3<u32>,
      @builtin(global_invocation_id) global_invocation_id : vec3<u32>,
      @builtin(local_invocation_index) local_invocation_index: u32,
      @builtin(num_workgroups) num_workgroups: vec3<u32>
    ) {
    let workgroup_index =  
       workgroup_id.x +
       workgroup_id.y * num_workgroups.x +
       workgroup_id.z * num_workgroups.x * num_workgroups.y;

    let global_invocation_index =
       workgroup_index * 32 +
       local_invocation_index;
    
    let theta = f32(input[global_invocation_index]);

    var draw = (500 + 400 * sin(radians(theta)));
    draw = draw / 1000 * (%d - 1) + %d;

    output[global_invocation_index] = draw;
}

""" % (domainNum, start)

thetas = np.array([theta for theta in range(0, 372, 12)])
print("thetas")
print(thetas)

out = compute_with_buffers({0: thetas}, {1: thetas.nbytes}, compute_uDraws_code, n = len(thetas))
# Select data from buffer at binding 1
uDraws = np.frombuffer(out[1], dtype=np.float32)
print(uDraws.tolist())
print(len(uDraws))

out = compute_with_buffers({0: thetas}, {1: thetas.nbytes}, compute_vDraws_code, n = len(thetas))
# Select data from buffer at binding 1
vDraws = np.frombuffer(out[1], dtype=np.float32)
print(vDraws.tolist())
print(len(vDraws))

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
var<storage, read_write> output: array<u32>;

@compute @workgroup_size(32)
fn main()
{
    let end = arrayLength(knots, read) - %d;
    
    // de Boor Algorithm
    for (var i = 0; i < length(uInputs, read); ++i)       // u 방향 b spline
    {
        
    }
    
    for (var i = 0; i < length(vInputs, read); ++i)       // v 방향 b spline
    {
        
    }
}

""" % (degree)

out = compute_with_buffers({0: uDraws, 1: vDraws, 2: serial_cps, 3: knots},
                           {4: thetas.nbytes}, compute_B_Spline_code, n = len(thetas))
# Select data from buffer at binding 4
bSplines = np.frombuffer(out[4], dtype=np.int32)
print(bSplines.tolist())
print(len(bSplines))

######################################################################################

bSplineList = calB_Spline(control_points, knots, degree, uDraws, vDraws)

print(bSplineList)

## vec2d 형태를 1차원 배열 형태로 직렬화해서 셰이더에 넘겨야 한다.
## 그 말은 출력할 때에도 반대로 해줘야 해야한다는 소리
## compute shader에서 어떤 것을 병렬처리로 계산해야 할 지 정해야 함 -> 아마 u방향, v방향 knot들에 대한 de boor 알고리즘일 듯