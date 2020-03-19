import time
import os

hostname = "192.168.0.202"

while True:
    response = os.system("ping -c 1 " + hostname)  

    if response == 0:   
        print(hostname, 'Reboot successful!')
        time.sleep(15)
        os.system("DISPLAY=:0  /usr/bin/chromium-browser --disable-session-crashed-bubble --disable-features=InfiniteSessionRestore  --disable-infobars --kiosk  http://192.168.0.202:9001/#/signin-token?token=2e981186e7d75f194ca9ef82e2b1f441edb5b42254ea14d3e725b03a1ebb29b7c570af39eefbab78e59588be18e1c6f41756ed0e9c192957dfd3cfce121a5b6b")
        break
    else:
        continue

while True:
    continue