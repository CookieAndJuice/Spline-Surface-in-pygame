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
control_points = np.array([[[minW + n * h, minH + a * h] for n in range(0, cpsWidth)] for a in range(0, cpsHeight)], dtype=np.float32)
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
knots = np.array([i for i in range(0, cpsWidth + degree - 1)], dtype=np.uint32)
print(knots)
print("")

# domain knots 계산
start = degree - 1              # domain 시작 지점
end = len(knots) - degree        # domain 끝 지점
domainNum = end - start + 1     # domain knots 개수

# 그릴 점 (u, v) - (start <= u, v <= end)     ## 원 -> 임의의 크기를 정해서 비율을 줄임
uDraws = np.array([int(500 + 400 * math.cos(math.radians(theta))) / 1000 * (domainNum - 1) + start for theta in range(0, 372, 12)], dtype=np.float32)
vDraws = np.array([int(500 + 400 * math.sin(math.radians(theta))) / 1000 * (domainNum - 1) + start for theta in range(0, 372, 12)], dtype=np.float32)
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

uIntervals = np.array(uIntervals, dtype=np.uint32)
vIntervals = np.array(vIntervals, dtype=np.uint32)

uResultLength = len(uDraws) * cpsHeight             # uResult의 크기

######################################################################################
# compute shader code
compute_shader_code = f"""
@group(0) @binding(0)
var<storage, read> uInputs: array<f32>;

@group(0) @binding(1)
var<storage, read> vInputs: array<f32>;

@group(0) @binding(2)
var<storage, read> control_points: array<vec2<f32>>;

@group(0) @binding(3)
var<storage, read> knots: array<u32>;

@group(0) @binding(4)
var<storage, read> uIntervals: array<u32>;

@group(0) @binding(5)
var<storage, read> vIntervals: array<u32>;

@group(0) @binding(6)
var<storage, read_write> output: array<f32>;

@compute @workgroup_size(32)
fn main(@builtin(global_invocation_id) global_invocation_id: vec3u)
{{
    
    let degree = u32({degree});
    let cpsWidth = u32({cpsWidth});
    let cpsHeight = u32({cpsHeight});
    let cpsNum = u32({cpsWidth});
    var uResult: array<vec2<f32>, {uResultLength}>;
    let index = global_invocation_id.x;
    
    // de Boor Algorithm
    // u 방향 계산 (계산 순서 : u 하나에 대해 모든 높이 계산 -> 다음 u 계산)
    let yOffset = cpsWidth;                                     // 높이값 넘어갈 때 offset
    
    let uInterval = uIntervals[index];
    var tempIndex = uInterval + 1;                              // 계산식에서 인덱스를 맞추기 위해 쓰는 임시 변수
    
    for (var height = 0u; height < cpsHeight; height++)
    {{
        let nowPos = height * yOffset;                          // 계산값 임시 저장 리스트
        var tempCps: array<vec2<f32>, {cpsWidth}>;
        for(var num = 0u; num < {cpsWidth}; num++)
        {{
            tempCps[num] = control_points[nowPos + num];
        }}
        
        for (var k = 1u; k < degree + 1; k++)
        {{
            let iInitial = uInterval - degree + k + 1;
            
            for (var i = uInterval + 1u; i > iInitial - 1u; i--)
            {{
                let alpha = (uInputs[index] - f32(knots[i - 1])) / f32(knots[i + degree - k] - knots[i - 1]);
                tempCps[i] = (1 - alpha) * tempCps[i - 1] + alpha * tempCps[i];
            }}
        }}
        uResult[index * cpsHeight + height] = tempCps[tempIndex];
    }}
    
    // v 방향 계산
    let xOffset = cpsHeight;                                    // 너비값 넘어갈 때 offset
    
    let vInterval = vIntervals[index];
    tempIndex = vInterval + 1;                              // 계산식에서 인덱스를 맞추기 위해 쓰는 임시 변수
    
    let nowPos = index * xOffset;                // 계산값 임시 저장 리스트
    var vTempCps: array<vec2<f32>, {cpsWidth}>;
    for(var num = 0u; num < {cpsWidth}; num++)
    {{
        vTempCps[num] = uResult[nowPos + num];
    }}
    
    for (var k = 1u; k < degree + 1; k++)
    {{
        let iInitial = vInterval - degree + k + 1;
        
        for (var i = vInterval + 1u; i > iInitial - 1u; i--)
        {{
            let alpha = (vInputs[index] - f32(knots[i - 1])) / f32(knots[i + degree - k] - knots[i - 1]);
            vTempCps[i] = (1 - alpha) * vTempCps[i - 1] + alpha * vTempCps[i];
        }}
    }}
    output[index] = vTempCps[tempIndex].x;
    output[index + 31] = vTempCps[tempIndex].y;
}}
"""

######################################################################################

# print("B-Spline 결과")
# bSplineList = calB_Spline(serial_cps, knots, uDraws, vDraws, uIntervals, vIntervals, cpsWidth, cpsHeight, degree)
# print(bSplineList)
# print("")

outLength = len(uDraws)
out = compute_with_buffers({0: uDraws, 1: vDraws, 2: serial_cps, 3: knots, 4: uIntervals, 5: vIntervals}, 
                           {6: (outLength*2, "f")}, compute_shader_code, n=1)
result = np.frombuffer(out[6], dtype=np.float32)
result = np.array(result, np.float64)

bSplineList = [np.array([result[a], result[a + outLength]], dtype=np.float64) for a in range(0, outLength)]
print(bSplineList)
print(bSplineList[0].dtype)
print(len(bSplineList))