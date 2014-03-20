# From "The Hard Way" of this answer:
# http://stackoverflow.com/a/309193

class ColourGenerator:
  patterns = [
    "{0}0000",
    "00{0}00",
    "0000{0}",
    "{0}{0}00",
    "{0}00{0}",
    "00{0}{0}",
    "{0}{0}{0}"
  ]

  def __init__(self):
    self.index = 0
    self.intensity_generator = IntensityGenerator()


  def get_next_RGB(self):
    # hex_to_rbg() is from here: http://stackoverflow.com/a/214657
    def hex_to_rgb(value):
      value = value.lstrip('#')
      lv = len(value)
      return tuple(int(value[i:i+lv/3], 16) for i in range(0, lv, lv/3))

    return hex_to_rgb(self.get_next_color())


  def get_next_color(self):
    pattern = self.get_next_pattern()
    intensity = self.intensity_generator.get_next_intensity(self.index)
    self.index += 1
    color = pattern.format(intensity)
    return color

  def get_next_pattern(self):
    return self.patterns[self.index % 7]


class IntensityGenerator:
  def __init__(self):
    self.walker = None
    self.current = None


  def get_next_intensity(self, i):
    if i == 0:
      self.current = 255

    elif i % 7 == 0:
      if self.walker is None:
        self.walker = IntensityValueWalker()
      else:
        self.walker.next()

      self.current = self.walker.current.value

    # Convert integer value to hexadecimal format, without the prefixed Ox.
    current = hex(self.current).lstrip("0x")
    if len(current) == 1:
      current = "0{0}".format(current)

    return current


class IntensityValue:
  def __init__(self, parent, v, level):
    self.mChildA = None
    self.mChildB = None

    self.value = v
    self.parent = parent
    self.level = level


  def get_childA(self):
    if self.mChildA is None:
      self.mChildA = IntensityValue(self, self.value - (1<<(7-self.level)), self.level+1)

    return self.mChildA


  def get_childB(self):
    if self.mChildB is None:
      self.mChildB = IntensityValue(self, self.value + (1<<(7-self.level)), self.level+1)

    return self.mChildB


class IntensityValueWalker:
  def __init__(self):
    self.current = IntensityValue(None, 1<<7, 1)


  def next(self):
    if self.current.parent is None:
      self.current = self.current.get_childA()

    elif self.current == self.current.parent.get_childA():
      self.current = self.current.get_childB()

    else:
      levels_up = 1
      self.current = self.current.parent

      while (
        self.current.parent is not None and
        self.current == self.current.parent.get_childB()
      ):
        self.current = self.current.parent
        levels_up += 1

      if self.current.parent is not None:
        self.current = self.current.parent.get_childB()
      else:
        levels_up += 1

      for i in range(levels_up):
        self.current = self.current.get_childA()


if __name__ == "__main__":
  generator = ColourGenerator()
  for i in range(896):
    print("{0}: {1}".format(i, generator.get_next_color()))

