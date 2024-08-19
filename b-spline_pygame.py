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

    
    result = []     # b spline 계산 결과
    
    # de Boor Algorithm
    for u in draws:
        if (u == knts[end]):
            interval = end - 1
        else:
            interval = findInterval(knts, u)            # knot interval 위치 찾기
        
        tempCount = 1                   # 계산식에서 인덱스를 맞추기 위해 쓰는 임시 변수
        tempCps = list(cps)             # 계산값 임시 저장 리스트 1
        temp = [vec2d(0, 0) for i in range(0, len(cps))]               # 계산값 임시 저장 리스트 2
        
        for k in range(1, degree + 1):      # degree 인덱스 k
            iInitial = interval - degree + k + 1   # control points 계산 결과들의 인덱스 i의 초기값 (degree마다 바뀜)
            
            for i in range(iInitial, interval + 2):    # i부터 최대값까지 반복 계산
                alpha = (u - knts[i - 1]) / (knts[interval + 1] - knts[i - 1])          # 계수
                
                temp[i - tempCount] = (1 - alpha) * tempCps[i - tempCount] + alpha * tempCps[i - tempCount + 1]         # 결과가 인덱스 0으로 모이도록 임시 저장
                
            tempCount += 1
            tempCps = list(temp)        # temp에 임시저장한 계산 결과를 tempCps로 옮김
            temp = [vec2d(0, 0) for i in range(0, len(cps))]
        
        tempCount = iInitial + 1 - tempCount
        result.append([int(tempCps[tempCount].x), int(tempCps[tempCount].y)])
        
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
    
    # Control Points
    control_points = [vec2d(853,1080), vec2d(640,560), vec2d(1280,288), vec2d(1920,560), vec2d(1707, 1080)]
    
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
                for p in control_points:
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
        for p in control_points:
            pygame.draw.circle(screen, BLACK, (int(p.x), int(p.y)), 4)
        
        pygame.draw.aalines(screen, BLACK, False, [(x.x, x.y) for x in control_points])
        
        bezierList = calB_Spline(control_points, knots, degree)
        pygame.draw.aalines(screen, BLUE, False, bezierList)
        
        pygame.display.flip()
        pygame.display.update()

    ## 종료 ##
    pygame.quit()
    sys.exit()

main()