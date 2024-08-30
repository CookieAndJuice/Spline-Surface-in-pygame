import pygame, sys
from pygame.locals import *
import math

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
    start = degree - 1          # domain 시작 지점
    end = len(knts) - degree    # domain 끝 지점
    
    # 그릴 점들 간의 간격, 그릴 점들
    h = (end - start) / numJoints
    draws = [h * a + knts[start] for a in range(0, numJoints + 1)]        # domain knots를 numJoints등분

    uResult = [[], [], [], []]      # u 방향 b spline 계산 결과
    result = []                     # b spline 계산 최종 결과
    
    # de Boor Algorithm
    for u in draws:         # u 방향 b spline
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

    for v in draws:         # v 방향 b spline
        if (v == knts[end]):
            interval = end - 1
        else:
            interval = findInterval(knts, v)            # knot interval 위치 찾기

        tempIndex = interval + 1                                        # 계산식에서 인덱스를 맞추기 위해 쓰는 임시 변수
        tempCps = [arr[:] for arr in uResult]                           # 계산값 임시 저장 리스트 1

        for width in range(0, len(tempCps[0])):
            temp = [vec2d(0, 0) for i in range(0, len(uResult))]            # 계산값 임시 저장 리스트 2

            for k in range(1, degree + 1):              # degree 인덱스 k
                iInitial = interval - degree + k + 1    # control points 계산 결과들의 인덱스 i의 초기값 (degree마다 바뀜)
                
                for i in range(iInitial, interval + 2):                                     # i부터 최대값까지 반복 계산
                    alpha = (v - knts[i - 1]) / (knts[i + degree - k] - knts[i - 1])        # 계수
                    
                    temp[i] = (1 - alpha) * tempCps[i - 1][width] + alpha * tempCps[i][width]         # 결과가 인덱스 (interval+1)로 모이도록 임시 저장
                
                for num in range(0, 4):
                    tempCps[num][width] = temp[num]        # temp에 임시저장한 계산 결과를 tempCps로 옮김
                temp = [vec2d(0, 0) for i in range(0, len(uResult))]
            
            result.append([int(tempCps[tempIndex][width].x), int(tempCps[tempIndex][width].y)])

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

    interval = screenHeight / 5
    startX = int(screenWidth / 2 - (interval * 3 / 2))
    startY = int(screenHeight / 2 - (interval * 3 / 2))
    
    # Control Points
    control_points = [[vec2d(startX,startY), vec2d(startX + interval,startY), vec2d(startX + interval*2,startY), vec2d(startX + interval*3,startY)],
                        [vec2d(startX,startY + interval), vec2d(startX + interval,startY + interval), vec2d(startX + interval*2,startY + interval), vec2d(startX + interval*3,startY + interval)],
                        [vec2d(startX,startY + interval*2), vec2d(startX + interval,startY + interval*2), vec2d(startX + interval*2,startY + interval*2), vec2d(startX + interval*3,startY + interval*2)],
                        [vec2d(startX,startY + interval*3), vec2d(startX + interval,startY + interval*3), vec2d(startX + interval*2,startY + interval*3), vec2d(startX + interval*3,startY + interval*3)]]

    # 그릴 점 (u, v) - (0 <= u, v <= 1)     ## 원 -> 임의의 크기를 정해서 비율을 줄임
    draw_points = [vec2d(int(500 + 400 * math.cos(math.radians(theta))) / 1000, int(500 + 400 * math.sin(math.radians(theta))) / 1000) for theta in range(0, 372, 12)]
    # for a in draw_points:
    #     print("(" + str(a.x) + ", " + str(a.y) + ")")
    
    # Degree
    degree = 3
    
    # knots
    knots = [i for i in range(0, len(control_points) + degree - 1)]

    ######################################################################################
    
    pygame.display.set_caption("Bezier Curve")
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
                for ps in control_points:
                    for p in ps:
                        if abs(p.x - event.pos[X]) < 10 and abs(p.y - event.pos[Y]) < 10 :
                            selected = p
            # elif event.type == MOUSEBUTTONDOWN and event.button == 3:
            #     x,y = pygame.mouse.get_pos()
            #     control_points.append(vec2d(x,y))
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                selected = None
                
        screen.fill(WHITE)
        
        if selected is not None:
            selected.x, selected.y = pygame.mouse.get_pos()
            pygame.draw.circle(screen, GREEN, (selected.x, selected.y), 10)
        
        ### Draw control points
        for ps in control_points:
            for p in ps:
                pygame.draw.circle(screen, BLACK, (int(p.x), int(p.y)), 4)
            pygame.draw.aalines(screen, BLACK, False, [(x.x, x.y) for x in ps])
        
        for i in range(0, 4):
            pygame.draw.aalines(screen, BLACK, False, [(control_points[j][i].x, control_points[j][i].y) for j in range(0, 4)])
        
        bSplineList = calB_Spline(control_points, knots, degree)
        # pygame.draw.aalines(screen, BLUE, False, bSplineList)

        for bPos in bSplineList:
            pygame.draw.circle(screen, BLUE, bPos, 4.0)
        
        pygame.display.flip()
        pygame.display.update()

    ## 종료 ##
    pygame.quit()
    sys.exit()

main()