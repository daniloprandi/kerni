# Linux User.

# Read Linux user information.

import pwd

# Return the username associated with a UID.
def get_username(uid):
  try:
    # Return the username.
    return pwd.getpwuid(uid).pw_name
  except KeyError:
    # Unknown user.
    return None