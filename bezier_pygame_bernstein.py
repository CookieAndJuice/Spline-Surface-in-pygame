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
# Bezier Curve

# Bernstein Basis Polynomial
def basisFunc(n, i, t):
    # 이항정리 계수
    coeff = math.factorial(n) / (math.factorial(i) * math.factorial(n - i))
    # Bernstein Polynomial 계산
    B = coeff * (t**i) * ((1-t)**(n-i))
    return B

def calBezierCurve(cps, numJoints=30):
    if numJoints < 2 or len(cps) != 4:
        return None
    
    result = []
    
    n = len(cps) - 1
    h = 1.0 / (numJoints)
    
    for i in range(0, numJoints + 1):
        resultVec = basisFunc(n, 0, h*i) * cps[0]
        resultVec += basisFunc(n, 1, h*i) * cps[1]
        resultVec += basisFunc(n, 2, h*i) * cps[2]
        resultVec += basisFunc(n, 3, h*i) * cps[3]
        
        result.append([int(resultVec.x), int(resultVec.y)])
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
    screenWidth = 1260
    screenHeight = 720
    size = (screenWidth, screenHeight)
    screen = pygame.display.set_mode(size)

    ## 선택한 점
    selected = None

    ## Control Points
    control_points = [vec2d(252,144), vec2d(504,144), vec2d(756,144), vec2d(1008,144)]
    # Bezier Curve를 나눈 개수
    CELLS = 30

    pygame.display.set_caption("Bezier Curve")
    clock = pygame.time.Clock()

    running = True
    while running:
        frame = clock.tick(60)
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
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
        
        bezierList = calBezierCurve(control_points, CELLS)
        pygame.draw.aalines(screen, BLUE, False, bezierList)
        
        pygame.display.flip()
        pygame.display.update()

    ## 종료 ##
    pygame.quit()
    sys.exit()

main()