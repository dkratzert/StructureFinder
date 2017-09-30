
import os
import platform

plat = platform.system()

if plat == 'windows':
    os.system("copy_windows_web.cmd")
else:
    os.system("sh ./mac_copyfiles.sh")

