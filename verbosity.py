class Verbosity(object):

  def __init__(self,level):
    self.level = level
    
  def print_(self,message):
    
    if self.level == 0:
      pass
      
    elif self.level == 1:
      print message
