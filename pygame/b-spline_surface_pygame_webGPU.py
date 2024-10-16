import pygame, sys
from pygame.locals import *
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

######################################################################################

def main():
    ## 컬러 세팅 ##
    BLUE = (0,0,255)
    RED = (255,0,0)
    GREEN = (0,255,0)
    BLACK = (0,0,0)
    WHITE = (255,255,255)
    LIGHTGRAY = (200,200,200)

    X,Y,Z = 0,1,2

    ## pygame app for figure to run ##
    pygame.init()

    ## screen setting ##
    screenWidth = 2560
    screenHeight = 1440
    size = (screenWidth, screenHeight)
    screen = pygame.display.set_mode(size)

    # 선택한 점
    selected = None
    
    ######################################################################################
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
    # control_points = [[vec2d(minW + n * h, minH + a * h) for n in range(0, cpsNum)] for a in range(0, cpsNum)]
    serial_cps = []
    for a in range(0, cpsHeight):
        for b in range(0, cpsWidth):
            serial_cps.append([minW + b * h, minH + a * h])
    serial_cps = np.array(serial_cps)

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

    # uResult의 크기
    uResultLength = len(uDraws) * cpsHeight
    outLength = len(uDraws)
    tempWidth = degree + 1                              # tempCps의 크기
    
    ######################################################################################
    # Compute Shader Code
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
        let tempWidth = degree + 1;
        let uInterval = uIntervals[index];
        let vInterval = vIntervals[index];
        
        // u 방향 계산 (계산 순서 : u 하나에 대해 모든 높이 계산 -> 다음 u 계산)
        let yOffset = cpsWidth;                                     // 높이값 넘어갈 때 offset
        
        for (var height = 0u; height < {tempWidth}; height++)
        {{
            let nowPos = (height + vInterval - degree + 1) * yOffset + (uInterval - degree + 1);        // iInitial - 1
            var tempCps: array<vec2<f32>, {tempWidth}>;                          // 계산값 임시 저장 리스트
            for(var num = 0u; num < {tempWidth}; num++)
            {{
                tempCps[num] = control_points[nowPos + num];
            }}
            
            for (var k = 1u; k < degree + 1; k++)
            {{
                let iInitial = uInterval - degree + k + 1;
                var uIntervalIndex = degree;
                
                for (var i = uInterval + 1u; i > iInitial - 1u; i--)
                {{
                    let alpha = (uInputs[index] - f32(knots[i - 1])) / f32(knots[i + degree - k] - knots[i - 1]);
                    tempCps[uIntervalIndex] = (1 - alpha) * tempCps[uIntervalIndex - 1] + alpha * tempCps[uIntervalIndex];
                    uIntervalIndex--;
                }}
            }}
            uResult[index * tempWidth + height] = tempCps[degree];
        }}
        
        // v 방향 계산
        let xOffset = tempWidth;                                    // 너비값 넘어갈 때 offset
        
        let nowPos = index * xOffset;                // 계산값 임시 저장 리스트
        var vTempCps: array<vec2<f32>, {tempWidth}>;
        for(var num = 0u; num < {tempWidth}; num++)
        {{
            vTempCps[num] = uResult[nowPos + num];
        }}
        
        for (var k = 1u; k < degree + 1; k++)
        {{
            let iInitial = vInterval - degree + k + 1;
            var vIntervalIndex = degree;
            
            for (var i = vInterval + 1u; i > iInitial - 1u; i--)
            {{
                let alpha = (vInputs[index] - f32(knots[i - 1])) / f32(knots[i + degree - k] - knots[i - 1]);
                vTempCps[vIntervalIndex] = (1 - alpha) * vTempCps[vIntervalIndex - 1] + alpha * vTempCps[vIntervalIndex];
                vIntervalIndex--;
            }}
        }}
        output[index] = vTempCps[degree].x;
        output[index + 31] = vTempCps[degree].y;
    }}
    """
    ######################################################################################
    
    pygame.display.set_caption("B Spline Curve")
    clock = pygame.time.Clock()

    running = True
    while running:
        frame = clock.tick(60)
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                for p in serial_cps:
                    if abs(p[0] - event.pos[X]) < 10 and abs(p[1] - event.pos[Y]) < 10 :
                        selected = p
                        print(selected == p)
            # elif event.type == MOUSEBUTTONDOWN and event.button == 3:
            #     x,y = pygame.mouse.get_pos()
            #     control_points.append(vec2d(x,y))
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                selected = None
                
        screen.fill(WHITE)
        
        if selected is not None:
            for p in serial_cps:
                if p[0] == selected[0] and p[1] == selected[1]:
                    selected = p
            selected[0], selected[1] = pygame.mouse.get_pos()
            pygame.draw.circle(screen, GREEN, (selected[0], selected[1]), 10)
        
        ### Draw control points
        for p in serial_cps:
            pygame.draw.circle(screen, BLACK, (int(p[0]), int(p[1])), 4)
            
        for y in range(0, cpsHeight):
            pygame.draw.aalines(screen, BLACK, False, [serial_cps[y * cpsWidth + x] for x in range(0, cpsWidth)])
        for x in range(0, cpsWidth):
            pygame.draw.aalines(screen, BLACK, False, [serial_cps[y * cpsWidth + x] for y in range(0, cpsHeight)])
        
        # B Spline Surface 계산
        serial_cps = serial_cps.astype('float32')
        out = compute_with_buffers({0: uDraws, 1: vDraws, 2: serial_cps, 3: knots, 4: uIntervals, 5: vIntervals}, 
                                   {6: (outLength*2, "f")}, compute_shader_code, n=1)
        result = np.frombuffer(out[6], dtype=np.float32)
        
        bSplineList = [[float(result[a]), float(result[a + outLength])] for a in range(0, outLength)]
        serial_cps = serial_cps.astype(float)
        
        pygame.draw.aalines(screen, BLUE, False, bSplineList)

        for bPos in bSplineList:
            pygame.draw.circle(screen, BLUE, bPos, 4.0)
        
        pygame.display.flip()
        pygame.display.update()

    ## 종료 ##
    pygame.quit()
    sys.exit()

main()

# 현재 webgpu의 타입과, python의 타입과 numpy의 타입이 서로 맞지 않아서 문제가 계속 발생함.
# webgpu에 의한 결과는 잘 나오지만 타입 변환 문제로 인해 문제가 발생.
# TypeError: center argument must be a pair of numbers

# 현재 결과가 이상한 이유
# 1. WebGPU의 int형과 float형은 최대 32bit다.
# 2. 파이썬의 기본 타입은 numpy로 보면 np.int64, np.float64다.
# 3. 이런 잦은 형변환을 pygame이 따라가지 못한다.
# 4. pygame에서 selected가 얕은 복사를 이용해서 포인터를 얻은 효과를 사용하기 때문이다.

# 해결 : 선택된 경우에 한해서 다시 할당해줬음

# 교수님 피드백
# 필요한 control points의 인덱스를 미리 계산해서 shader로 넘겨주기. 
# 나의 경우 uInterval, vInterval에 따라서 인덱스가 달라지도록 만들면 인덱스 배열 크기를 줄일 수 있을 듯
# 5x5를 이용하는 게 아니라 4x4를 이용한다고 생각해야 함

# 앞으로 할 일
# 1. b spline surface를 온전히 webgpu로 옮기는 것
# 2. 3d b spline surface 구현 (normal vector도 계산해야 하기 때문에 한 vertex와 인접한 vertices를 가져와야 해서 복잡해진다.)