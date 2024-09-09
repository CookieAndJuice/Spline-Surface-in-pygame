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
# Bezier Surface De Casteljau

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
    
    # n = len(cps) - 1
    # h = 1.0 / (numJoints)
    
    # print(n, h)
    
    for t in drawPoints:        # drawPoints에 있는 t = (u,v) 이용
        uPoints = [arr[:] for arr in cps]
        
        for height in range(0, 4):      # u 방향으로 베지어 곡선 만듦
            for i in range(3, -1, -1):
                for re in range(0, i):
                    uPoints[height][re] = linearInterpolate(t.x, uPoints[height][re], uPoints[height][re + 1])

            resultU[height].append(uPoints[height][0])
    
    # u에 의한 값들 중간 점검
    for ind in range(0, len(resultU)):
        for idx in range(0, len(resultU[ind])):
            print("(" + str(resultU[ind][idx].x) + ", " + str(resultU[ind][idx].y) + ")", end = ", ")
            
    for t in range(0, len(drawPoints)):         # v 방향으로 베지어 곡선 만듦
        uPoints = [arr[:] for arr in resultU]       # u 방향으로 찍어놓은 점들을 가지고 옴
        
        for i in range(3, -1, -1):
            for height in range(0, i):
                uPoints[height][t] = linearInterpolate(drawPoints[t].y, uPoints[height][t], uPoints[height + 1][t])
        print("height : " + str(height) + ", " + str(uPoints[height][t].y))

        result.append([int(uPoints[0][t].x), int(uPoints[0][t].y)])
        
    print(len(result))
    return result

######################################################################################

# Control Points
control_points = [[vec2d(414,144), vec2d(558,144), vec2d(702,144), vec2d(846,144)],
                    [vec2d(414,288), vec2d(558,288), vec2d(702,288), vec2d(846,288)],
                    [vec2d(414,432), vec2d(558,432), vec2d(702,432), vec2d(846,432)],
                    [vec2d(414,576), vec2d(558,576), vec2d(702,576), vec2d(846,576)]]
draw_points = [vec2d(int(500 + 400 * math.cos(math.radians(theta))) / 1000, int(500 + 400 * math.sin(math.radians(theta))) / 1000) for theta in range(0, 372, 12)]

for a in draw_points:
    print("(" + str(a.x) + ", " + str(a.y) + ")")

bezierList = calBezierSurface(control_points, draw_points)

print(bezierList)