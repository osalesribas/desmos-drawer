import cv2
import numpy as np

# EDIT THESE:
IMAGE_PATH = 'Examples/Source/Camp Nou.png' # Edit this to change the image path
INACCURACY_VALUE = 0.002; # adjust this to change the accuracy of the approximation. The lower, the more accurate but the more equations. It is recommended not to go over 0.03 (3%), but feel free to experiment.



image = cv2.imread(IMAGE_PATH, 1)
img_height = image.shape[0]

edges = cv2.Canny(image, 100, 200)

contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

def bezier_to_equations(start, c1, c2, end, img_height):
    """Convert cubic Bezier curve control points to parametric equations to be represented in Desmos."""

    start = (start[0], img_height - start[1]) # img_height - X inverts y to follow coordinate system.
    c1 = (c1[0], img_height - c1[1])
    c2 = (c2[0], img_height - c2[1])
    end = (end[0], img_height - end[1])

    equation_x = f"((1-t)^3*{start[0]} + 3*(1-t)^2*t*{c1[0]} + 3*(1-t)*t^2*{c2[0]} + t^3*{end[0]})"
    equation_y = f"(1-t)^3*{start[1]} + 3*(1-t)^2*t*{c1[1]} + 3*(1-t)*t^2*{c2[1]} + t^3*{end[1]}"
    return equation_x, equation_y

with open("equations.txt", "w") as f:
    for contour in contours:
        epsilon = INACCURACY_VALUE * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        for i in range(len(approx)):
            start = approx[i][0]
            end = approx[(i+1) % len(approx)][0]
            
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            
            if dx == 0: # a vertical line
                    f.write(f"x = {start[0]} \\left\\{{{img_height - max(start[1], end[1])} <= y <= {img_height - min(start[1], end[1])}\\right\\}}\n")
            elif dy == 0: # a horizontal line
                f.write(f"y = {img_height - start[1]} \\left\\{{{min(start[0], end[0])} <= x <= {max(start[0], end[0])}\\right\\}}\n")
        
            else: # a curve
                c1 = (2*start[0] + end[0]) / 3, (2*start[1] + end[1]) / 3
                c2 = (start[0] + 2*end[0]) / 3, (start[1] + 2*end[1]) / 3
                
                eq_x, eq_y = bezier_to_equations(start, c1, c2, end, img_height)
                f.write(f"({eq_x}, {eq_y})\n")
