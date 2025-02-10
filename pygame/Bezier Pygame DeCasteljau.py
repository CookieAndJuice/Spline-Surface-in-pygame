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
# Bezier Surface

# 선형 보간
def linearInterpolate(t, pointA, pointB):
    resPoint = (1-t) * pointA + t * pointB
    return resPoint

# Cubic
def calBezierSurface(cps, drawPoints):
    if len(cps) != 4:
        return None
    
    resultU = [[], [], [], []]
    result = []
    
    for t in drawPoints:        # drawPoints에 있는 t = (u,v) 이용
        uPoints = [arr[:] for arr in cps]
        
        for height in range(0, 4):      # u 방향으로 베지어 곡선 만듦
            for i in range(3, -1, -1):
                for re in range(0, i):
                    uPoints[height][re] = linearInterpolate(t.x, uPoints[height][re], uPoints[height][re + 1])

            resultU[height].append(uPoints[height][0])
            
    for t in range(0, len(drawPoints)):         # v 방향으로 베지어 곡선 만듦
        uPoints = [arr[:] for arr in resultU]       # u 방향으로 찍어놓은 점들을 가지고 옴
        
        for i in range(3, -1, -1):
            for height in range(0, i):
                uPoints[height][t] = linearInterpolate(drawPoints[t].y, uPoints[height][t], uPoints[height + 1][t])

        result.append([int(uPoints[0][t].x), int(uPoints[0][t].y)])
        
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
        
        bezierList = calBezierSurface(control_points, draw_points)
        
        # pygame.draw.aalines(screen, BLUE, False, bezierList)
        for point in bezierList:
            pygame.draw.circle(screen, BLUE, point, 4.0)
        
        pygame.display.flip()
        pygame.display.update()

    ## 종료 ##
    pygame.quit()
    sys.exit()

main()