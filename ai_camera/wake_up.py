import sys
from threading import Thread

sys.path.append('/home/pi/Wake_up_genie/python')
print(sys.path)

import call_genie as cg
import ai_eye_blink as eb


t = Thread(target=cg.main)
th = Thread(target=eb.main)
t.deamon = True
th.deamon = True
t.start()
th.start()
