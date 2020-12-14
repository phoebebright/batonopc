'''
to registr device with tinycloud, enter pin.
confirm pin is valid and will get gateway key in return
use gateway key to make quarantine request
'''
import requests
import os
import json




def getserial():
  # Extract serial from cpuinfo file
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "ERROR000000000"

  return cpuserial



def save_gatewaykey(key):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../gateway_key.txt")


    with open(path, 'w+') as out_file:
       data = json.loads(key)
       out_file.write(data['key'])


pin = input("Enter pin: ")

api = "https://thegascloud.com/api/v1/activate/"
payload = {'device_id' : getserial(),
           'pin': pin,
           'name': "Raspberry pi"}


response = requests.post(api, payload)

if response.status_code == 200:

    save_gatewaykey(response.content)

    print("Gateway has been activated")


else:
   print("ACTIVATION FAILED: %s" % response.reason)


def getserial():
  # Extract serial from cpuinfo file
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "ERROR000000000"

  return cpuserial