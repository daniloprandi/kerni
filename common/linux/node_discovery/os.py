import platform


def get_name():
  return platform.system()

def get_version():
  return platform.release()