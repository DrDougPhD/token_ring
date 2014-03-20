import math
Y_RES = 800

# Make the x-resolution big enough to hold one hexagon with two sides aligned
#  with the y-axis.
X_RES = int(math.ceil(Y_RES*math.sin(math.pi/3)))

