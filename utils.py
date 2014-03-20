import random
from settings import X_RES
from settings import Y_RES


def transform_points_for_pygame(points):
  return [(p[0], Y_RES - p[1]) for p in points]


def is_column_vector(v):
  # v := a numpy array
  return 1 == v.shape[1]


def RANDOM_COLOR():
  return [random.randint(0, 255) for i in range(3)]
