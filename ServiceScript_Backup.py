import random
import json
from websocket import create_connection
import time
import os
import stomper
from datetime import date
import timeout_decorator
import uuid 
mac_address = '_'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])
print(mac_address)

# import FakeRPi.GPIO as GPIO
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)

GPIO.output(17,1)
GPIO.output(27,1)
GPIO.output(22,1)
    
import multiprocessing.pool
import functools


# hostname = "192.168.0.202"
# 
# while True:
#     response = os.system("ping -c 1 " + hostname)  
# 
#     if response == 0:   
#         print(hostname, 'Reboot successful!')
#         time.sleep(10)
#         os.system("/usr/bin/chromium-browser --disable-session-crashed-bubble --disable-features=InfiniteSessionRestore  --disable-infobars --kiosk  http://192.168.0.202:9001/#/signin-token?token=2e981186e7d75f194ca9ef82e2b1f441edb5b42254ea14d3e725b03a1ebb29b7c570af39eefbab78e59588be18e1c6f41756ed0e9c192957dfd3cfce121a5b6b")
#         break
#     else:
#         continue
    
def Logging(string, response, server):
    line = (string + ' - ' + str(time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime()))
                + " - studenId: " + str(response['studentId'])
                + " - roomId: " + str(response['roomId'])
                + " - shiftCode: " + str(response['shiftCode'])
                + " - nvrId: " + str(response['nvrId'])
                + " - cameraId: " + str(response['cameraId'])
                + " - Server Websocket: " + str(server['server_websocket']))
    print(line)
    f = open('/home/pi/Scripts/Logs/'+ date.today().strftime("%d-%m-%y")+ '.log','a') # Ghi log theo tung ngay
    f.writelines(line + "\n")
    f.close()

# Log ngắn gọn hơn
def Log1(string, response, server):
    line = (string + ' - ' + str(time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime()))
                + " - studenId: " + str(response['studentId'])
                + " - roomId: " + str(response['roomId'])
                + " - shiftCode: " + str(response['shiftCode'])
                + " - nvrId: " + str(response['nvrId'])
                + " - cameraId: " + str(response['cameraId']))
    print(line)
    f = open('/home/pi/Scripts/Logs/'+ date.today().strftime("%d-%m-%y")+ '.log','a') # Ghi log theo tung ngay
    f.writelines(line + "\n")
    f.close()


def Log2(string):
    line = (string)
    print(line)
    # f = open('/home/pi/Scripts/Logs/'+ date.today().strftime("%d-%m-%y")+ '.log','a') # Ghi log theo tung ngay
    # f.writelines(line + "\n")
    # f.close()

def Connect(server):
    Log2("Connecting SmartAccess: "+ server['server_websocket'] + "....")
    ws = create_connection("ws://"+server['server_websocket'])
    sub = stomper.subscribe(server['topic1'], str(random.randint(0, 1000)), ack='auto')
    ws.send(sub)
    sub = stomper.subscribe(server['topic2'], str(random.randint(0, 1000)), ack='auto')
    ws.send(sub)
    Log2("--------------- Connect Successfully!")
    return ws

def Receive(ws):
    Log2("+ Waiting for data ....")
    response = str(ws.recv())
    return json.loads(response[response.find("{"):-1])

def Open_door(response, server):
    GPIO.output(17,0)
    GPIO.output(27,0)
    GPIO.output(22,0)
    Logging("-- OPENED DOOR", response, server) 

def Close_door(response, server):
    GPIO.output(17,1)
    GPIO.output(27,1)
    GPIO.output(22,1)
    Log2("-- CLOSED DOOR") 

def Open_Check(response, data, server):
    print('Data received: cameraId: ' + response['cameraId'] + ' - shiftCode: ' + str(response['shiftCode']))
    
    if response['shiftCode'] == None  or 1:
        if response['cameraId'] in data['cameraId'].replace(" ","").split(","):
            Open_door(response, server)
            start = time.time()

            person = True
            while person:
                try:
                    person = Check()
                except:
                    person = False

            print("Total time open door: ", time.time() - start, " seconds")

def Get_config_file():
    while True:
        try:
            with open('/home/pi/Scripts/server.txt') as f:
                server = json.load(f)
            with open('/home/pi/Scripts/dc_a6_32_1a_88_39.txt') as f:
                data = json.load(f)
            return server, data
        except:
            Log2("Updating config file...")
            continue

if __name__ == '__main__':
    
    server, data = old_server, old_data = Get_config_file()
    ws = Connect(server)

    while True:
        server, data = Get_config_file()

        @timeout_decorator.timeout(int(data['door_open']))
        def Check():
            print("Wait " + data['door_open'] + "sec for data ....")
            response = str(ws.recv())
            response = json.loads(response[response.find("{"):-1])
            if response['shiftCode'] == None or 1:
                if response['cameraId'] in data['cameraId'].replace(" ","").split(","):
                    Log1("More 5sec for: ", response, server)
                    return True
            return False

        @timeout_decorator.timeout(int(data['safe_time']))
        def Safe():
            Log2("Thời gian đóng an toàn " + data['safe_time'] + "s bắt đầu ....")
            while True:
                response = str(ws.recv())
                response = json.loads(response[response.find("{"):-1])
                if response['shift Code'] == None  or 1:
                    if response['cameraId'] in data['cameraId'].replace(" ","").split(","):
                        Log1('Đóng an toàn không mở: ', response, server)

        @timeout_decorator.timeout(int(data['update_config'])) # Nếu cửa không mở Sau 5min * 60sec = 300sec chạy lại 1 kết nối
        def main(ws):
            response = Receive(ws)
            Open_Check(response, data, server)
            Close_door(response, server)
            try:
                Safe()
            except:
                print("* * *")

        if server == old_server and data == old_data:
            try:
                main(ws)
            except:
                Log2(" >>> Cập nhật lại config sau 5 phút")
        else:
            old_server, old_data = server, data # Cập nhật lại thông số config chờ so sánh lần sau
            ws = Connect(server)
