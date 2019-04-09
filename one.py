# try:
import ptvsd
ptvsd.enable_attach(('0.0.0.0', 5679))
ptvsd.wait_for_attach()
# except Exception:
# 	pass


import sys

print(sys.path)
print(sys.executable)
