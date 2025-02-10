import pygame, sys
from pygame.locals import *
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
def calB_Spline(cps, knts, uDraws, vDraws, uIntervals, vIntervals, cpsWidth, degree):
    
    uResult = []                            # u 방향 계산 결과
    result = []                             # b spline 계산 최종 결과

    # de Boor Algorithm
    tempWidth = degree + 1                  # 매 u와 v마다 tempcps의 길이

    # u 방향 계산 (계산 순서 : u 하나에 대해 모든 높이 계산 -> 다음 u 계산)
    yOffset = cpsWidth                      # 높이값 넘어갈 때 offset
    
    for drawNum in range(0, len(uDraws)):
        uInterval = uIntervals[drawNum]
        vInterval = vIntervals[drawNum]
        
        for height in range(0, tempWidth):
            nowPos = (height + vInterval - degree + 1) * yOffset + (uInterval - degree + 1)               # iInitial - 1
            tempCps = np.array([cps[nowPos + num] for num in range(0, tempWidth)])       # 계산값 임시 저장 리스트
            
            print(tempCps[0], tempCps[1], tempCps[2], tempCps[3])
            
            for k in range(1, degree + 1):                                                          # degree 인덱스 k
                iInitial = uInterval - degree + k + 1                                                # control points 계산 결과들의 인덱스 i의 초기값 (degree마다 바뀜)
                intervalIndex = degree                                                           # tempCps의 범위는 0 ~ degree이다.

                alpha = 0
                for i in range(uInterval + 1, iInitial - 1, -1):                                             # i부터 최대값까지 반복 계산
                    alpha = (uDraws[drawNum] - knts[i - 1]) / (knts[i + degree - k] - knts[i - 1])           # 계수
                    tempCps[intervalIndex] = (1 - alpha) * tempCps[intervalIndex - 1] + alpha * tempCps[intervalIndex]      # 결과가 마지막 인덱스로 모이도록 임시 저장
                    intervalIndex -= 1
                print(alpha)
                
            print(tempCps[degree])
            uResult.append(tempCps[degree])             # tempCps 마지막 인덱스 추가
    
    # v 방향 계산
    xOffset = tempWidth                     # 너비값 넘어갈 때 offset. uResult 기준이어야 하므로, cps를 따라가지 않고 tempWidth를 따라간다
    
    for drawNum in range(0, len(vDraws)):
        interval = vIntervals[drawNum]
        
        nowPos = drawNum * xOffset                                          # uResult가 0~4 / 5~9 / ... 단위로 묶여서 단위마다 x값이 증가함. 단위 내에서는 y값 증가.
        tempCps = np.array([uResult[nowPos + num] for num in range(0, tempWidth)])       # 계산값 임시 저장 리스트
        
        for k in range(1, degree + 1):                                                          # degree 인덱스 k
            iInitial = interval - degree + k + 1                                                # control points 계산 결과들의 인덱스 i의 초기값 (degree마다 바뀜)
            intervalIndex = degree                                                              # tempCps의 범위는 0 ~ degree이다.
            
            for i in range(interval + 1, iInitial - 1, -1):                                             # i부터 최대값까지 반복 계산
                alpha = (vDraws[drawNum] - knts[i - 1]) / (knts[i + degree - k] - knts[i - 1])           # 계수
                tempCps[intervalIndex] = (1 - alpha) * tempCps[intervalIndex - 1] + alpha * tempCps[intervalIndex]      # 결과가 마지막 인덱스로 모이도록 임시 저장
                intervalIndex = intervalIndex - 1
            
        result.append(tempCps[degree])              # tempCps 마지막 인덱스 추가
        
    return result

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
    knots = np.array([i for i in range(0, cpsWidth + degree - 1)])
    
    # domain knots 계산
    start = degree - 1              # domain 시작 지점
    end = len(knots) - degree        # domain 끝 지점
    domainNum = end - start + 1     # domain knots 개수

    # 그릴 점 (u, v) - (start <= u, v <= end)     ## 원 -> 임의의 크기를 정해서 비율을 줄임
    uDraws = np.array([int(500 + 400 * math.cos(math.radians(theta))) / 1000 * (domainNum - 1) + start for theta in range(0, 372, 12)])
    vDraws = np.array([int(500 + 400 * math.sin(math.radians(theta))) / 1000 * (domainNum - 1) + start for theta in range(0, 372, 12)])

    # interval lists
    uIntervals = []
    for u in uDraws:
        interval = 0
        if (u == knots[end]):
            interval = end - 1
        else:
            interval = findInterval(knots, u)
        uIntervals.append(interval)

    vIntervals = []
    for v in vDraws:
        interval = 0
        if (v == knots[end]):
            interval = end - 1
        else:
            interval = findInterval(knots, v)
        vIntervals.append(interval)
        
    uIntervals = np.array(uIntervals)
    vIntervals = np.array(vIntervals)

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
        
        serial_cps = serial_cps.astype('float32')
        serial_cps = serial_cps.astype(float)
        
        # B Spline Surface 계산
        bSplineList = calB_Spline(serial_cps, knots, uDraws, vDraws, uIntervals, vIntervals, cpsWidth, degree)
        pygame.draw.aalines(screen, BLUE, False, bSplineList)
        
        for bPos in bSplineList:
            pygame.draw.circle(screen, BLUE, bPos, 4.0)
        
        pygame.display.flip()
        pygame.display.update()

    ## 종료 ##
    pygame.quit()
    sys.exit()

main()