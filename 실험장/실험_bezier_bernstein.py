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
    
    print(n, h)
    
    for i in range(0, numJoints + 1):
        resultVec = basisFunc(n, 0, h*i) * cps[0]
        resultVec += basisFunc(n, 1, h*i) * cps[1]
        resultVec += basisFunc(n, 2, h*i) * cps[2]
        resultVec += basisFunc(n, 3, h*i) * cps[3]
        
        result.append([int(resultVec.x), int(resultVec.y)])
    print(len(result))
    return result

######################################################################################

CELLS = 30
control_points = [vec2d(100,100), vec2d(150,500), vec2d(450,500), vec2d(500,150)]
bezierList = calBezierCurve(control_points, CELLS)

print(bezierList)