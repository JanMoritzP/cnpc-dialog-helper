import cmath
import math
from typing import List
from math import copysign, sqrt, cos, sin, atan2, pi

def getArrow(start: List[int], target: List[int]) -> List[int]:
    """Get the start and end vector of
    an arrow between two rectangles, so that the arrow
    does not cross throught the rectangles"""
    # start (x1, y1, x2, y2) target (x1, y1, x2, y2)

    startMid = abs(start[0] - start[2])/2 + start[0], abs(start[1] - start[3])/2 + start[1]
    targetMid = abs(target[0] - target[2])/2 + target[0], abs(target[1] - target[3])/2 + target[1]

    startX, startY = startMid #Initialize the values to catch the s = 0, c = 0 edge case
    targetX, targetY = targetMid

    x, y = targetMid[0] - startMid[0], targetMid[1] - startMid[1]
    
    width, height = abs(start[0] - start[2]), abs(start[1] - start[3])

    theta = atan2(y, x)

    c = cos(theta)
    s = sin(theta)
    if width * abs(s) < height * abs(c) and c != 0:
        startX = copysign(1, c) * (width/2) + startMid[0]
        startY = s/c * copysign(1, c) * (width/2) + startMid[1]
    elif s != 0:
        startY = copysign(1, s) * (height/2) + startMid[1]
        startX = c/s * copysign(1, s) * (height/2) + startMid[0]
    
    width, height = abs(target[0] - target[2]), abs(target[1] - target[3])
    theta = atan2(-y, -x)

    c = cos(theta)
    s = sin(theta)
    
    if width * abs(s) < height * abs(c) and c != 0:
        targetX = copysign(1, c) * (width/2) + targetMid[0]
        targetY = s/c * copysign(1, c) * (width/2) + targetMid[1]
    elif s != 0:
        targetY = copysign(1, s) * (height/2) + targetMid[1]
        targetX = c/s * copysign(1, s) * (height/2) + targetMid[0]

    return [startX, startY], [targetX, targetY]

    
def getOuterRectPos(start: List[int], target: List[int]) -> List[int]:
    """Get the outer position of a rectangle for a given rectangle and a connecting x, y coordinate"""
    # start (x1, y1, x2, y2) target (x1, y1)

    startMid = abs(start[0] - start[2])/2 + start[0], abs(start[1] - start[3])/2 + start[1]
    targetMid = target[0], target[1]

    startX, startY = startMid #Initialize the values to catch the s = 0, c = 0 edge case
    targetX, targetY = targetMid

    x, y = targetMid[0] - startMid[0], targetMid[1] - startMid[1]
    
    width, height = abs(start[0] - start[2]), abs(start[1] - start[3])

    theta = atan2(y, x)

    c = cos(theta)
    s = sin(theta)
    if width * abs(s) < height * abs(c) and c != 0:
        startX = copysign(1, c) * (width/2) + startMid[0]
        startY = s/c * copysign(1, c) * (width/2) + startMid[1]
    elif s != 0:
        startY = copysign(1, s) * (height/2) + startMid[1]
        startX = c/s * copysign(1, s) * (height/2) + startMid[0]

    return [startX, startY]