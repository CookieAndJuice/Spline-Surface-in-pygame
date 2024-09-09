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
# Bezier De Casteljau

# 선형 보간
def linearInterpolate(t, pointA, pointB):
    resPoint = (1-t) * pointA + t * pointB
    return resPoint

# Cubic
def calBezierCurve(cps, numJoints=30):
    if numJoints < 2 or len(cps) != 4:
        return None
    
    result = []
    tPoints = []
    
    n = len(cps) - 1
    h = 1.0 / (numJoints)
    
    print(n, h)
    
    for t in range(0, numJoints + 1):
        tPoints = list(cps)
        for i in range(3, -1, -1):
            for re in range(0, i):
                tPoints[re] = linearInterpolate(t * h, tPoints[re], tPoints[re + 1])

        result.append([int(tPoints[0].x), int(tPoints[0].y)])
    
    print(len(result))
    return result

######################################################################################

CELLS = 30
control_points = [vec2d(252,144), vec2d(504,144), vec2d(756,144), vec2d(1008,144)]
bezierList = calBezierCurve(control_points, CELLS)

print(bezierList)