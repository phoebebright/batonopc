'''
links that might be useful
https://www.hackster.io/john-brohan/headless-raspberry-pi-health-monitor-for-paraplegics-19ee2a
d costs half the price of the BlueMaestro.

The approach we have taken here is not perfect, it's not even good, but it does extract the data accurately and should work properly for any client who just buys one (of these two models) and turns it on near his head. No need to identify it.

The actual calls to read ble data usually use characteristics and rely on a connection. With Beacons there may be no connection, just pick off the airwaves their advertising packets and use them if they are the right ones. There may be many other advertisers, but our solution is limited to having only one each of these beacons within range (maybe later we will improve this).

The program structure is a s follows.
- prepare the bluetooth adapter on the raspberry pi device.
- run hcitool lescan and hcidump --raw periodically to capture the advertising packets being emitted locally, store these into the ramdisk.
The way this works is that hcitool lescan identifies the beacons and opens a pathway inside the bluetooth adapter to listen for those advertising packets.
sudo hcidump captures these advertising packets and with the --raw > /mnt/ramdisk/hcidump.txt &' command writes all the advertising packets it sees to the ramdisk.
The pid for each command is obtained and the process killed after 1 sec. Note the maximum delay between advertising packets of the BlueMaestro is 800ms, so 1s delay is ample.

At this point we have the /mnt/ramdisk/hcidump.txt file containing all those advertising packets. The next step is to go through them and pick out the appropriate ones for our sensors and then locate the data points and convert these into decimal and output these as strings to /mnt/ramdisk/MandT.txt and /mnt/ramdisk/MandT2.txt
The readem() function basically assembles the packets from the lines using the fact that the first char of a packet output by hcidump is ">".
The packets are scanned for the device id and then when this is found the temperature and moisture is extracted.

I do not reccommend this approach and would be delighted for someone to show me a wiser approach to getting data from beacons.

import time
import os
import subprocess
import commands
import re

mjDevice = ""
def getPid(process):
	pid = subprocess.check_output(["pidof","-s",process])
	return pid

def gettem():
	cmd1 = 'hcitool lescan --duplicates > /dev/null &'
	cmd2="sudo kill -15 "
	cmd3 = 'sudo hcidump --raw  > /mnt/ramdisk/hcidump.txt &'
	os.system(cmd3)

	time.sleep(0.5)
	os.system (cmd1)
	time.sleep(1)
	pid = getPid('hcitool')
	#print("pid found  ",pid)
	#print (cmd2 + pid)
	os.system(cmd2 + pid)
	time.sleep(0.5)
	#print("stop Dump")
	pidDump = getPid('hcidump')
	#print("pidDump found  ",pidDump)
	#print (cmd2 + pidDump )
	os.system(cmd2 + pidDump)

def readem():
	global mjDevice
	with open("/mnt/ramdisk/hcidump.txt") as f:
		packet = ""
		count = 0
		for line in (f):
			if line[0] == '>':
				packet = re.sub(r"[\n\t\s]*", "", packet)
				#print " ",packet
				if "33011764" in packet:
					temperature = packet[55:59]
					temp = float(eval("0x"+temperature)/10.0)
					#print temp
					moisture   =  packet[59:63]
					moist = float(eval("0x"+moisture)/10.0)
					#print moist
					fout = open( "/mnt/ramdisk/MandT.txt", 'w' )
					fout.write( "&t1="+str(temp) + '&m1=' + str(moist) + '\n' )
					fout.close()
				if "4D4A5F48545F5631" in packet:
					mjDevice = packet[15:27]
					#print "f",packet
					#print mjDevice
				if mjDevice in packet and mjDevice != "":
					if mjDevice + "0D1004" in packet:
						#print "got One"
						search = mjDevice + "0D1004"
						#print "search", search
						pos = packet.find(search)
						if pos > -1:
							#print packet
							#print "pos", pos
							#print packet[pos:pos+8]
							temperature = packet[pos+18+2:pos+18+2+2] + packet[pos+18:pos+18+2]
							moisture    = packet[pos+22+2:pos+22+2+2] + packet[pos+22:pos+22+2]
							#print "t", temperature, "m", moisture
							temp2  = float(eval("0x"+temperature)/10.0)
							moist2 = float(eval("0x"+moisture)/10.0)
							fout2= open( "/mnt/ramdisk/MandT2.txt", 'w' )
							fout2.write( "&t2="+str(temp2) + '&m2=' + str(moist2) + '\n' )
							fout2.close()
				packet = ""
			packet = packet + line

print " this program reads a Blue Maestro Moisture meter"
print " and writes the Temp and Moist as floats 5.1 to  "
print " the ramdisk file /mnt/ramdisk/MandT.txt where it "
print " can be read by darshan.py to send to the database."
one = 1
while one > 0:
	os.system("sudo hciconfig hci0 down")
	os.system("sudo hciconfig hci0 up")
	gettem()
	readem()
	time.sleep(60)




https://usermanual.wiki/Document/TemperatureHumidityDataLoggerCommandsAPI24.2837071165/help

'''


# BlueMastro Tempo Disc Advertising packet decoder
# Called from bluemaestro.py
# This class has the specificis for decoding the advertising packets for the Blue Maestro Tempo Disc https://www.bluemaestro.com/product/tempo-disc-temperature/
# Unsure if there are any other Blue Maestro products that it would work with.
# David@andc.nz 15/12/2016

DEBUG = True

# BLE Scanner based on from JCS 06/07/14
# BLE scanner based on https://github.com/adamf/BLE/blob/master/ble-scanner.py
# BLE scanner, based on https://code.google.com/p/pybluez/source/browse/trunk/examples/advanced/inquiry-with-rssi.py

# https://github.com/pauloborges/bluez/blob/master/tools/hcitool.c for lescan
# https://kernel.googlesource.com/pub/scm/bluetooth/bluez/+/5.6/lib/hci.h for opcodes
# https://github.com/pauloborges/bluez/blob/master/lib/hci.c#L2782 for functions used by lescan

# performs a simple device inquiry, and returns a list of ble advertizements 
# discovered device

# NOTE: Python's struct.pack() will add padding bytes unless you make the endianness explicit. Little endian
# should be used for BLE. Always start a struct.pack() format string with "<"

# Modified 2019-06 by JWJ:
#	- now returns an array of objects with temp, humidity, dewpoint, so multiple devices/advertisements can be found

import collections
import os
import sys
import struct
import bluetooth._bluetooth as bluez

LE_META_EVENT = 0x3e
LE_PUBLIC_ADDRESS = 0x00
LE_RANDOM_ADDRESS = 0x01
LE_SET_SCAN_PARAMETERS_CP_SIZE = 7
OGF_LE_CTL = 0x08
OCF_LE_SET_SCAN_PARAMETERS = 0x000B
OCF_LE_SET_SCAN_ENABLE = 0x000C
OCF_LE_CREATE_CONN = 0x000D

LE_ROLE_MASTER = 0x00
LE_ROLE_SLAVE = 0x01

# these are actually subevents of LE_META_EVENT
EVT_LE_CONN_COMPLETE = 0x01
EVT_LE_ADVERTISING_REPORT = 0x02
EVT_LE_CONN_UPDATE_COMPLETE = 0x03
EVT_LE_READ_REMOTE_USED_FEATURES_COMPLETE = 0x04

# Advertisment event types
ADV_IND = 0x00
ADV_DIRECT_IND = 0x01
ADV_SCAN_IND = 0x02
ADV_NONCONN_IND = 0x03
ADV_SCAN_RSP = 0x04


def returnnumberpacket(pkt):
    myInteger = 0
    multiple = 256
    for c in pkt:
        myInteger += struct.unpack("B", c)[0] * multiple
        multiple = 1
    return myInteger


def returnstringpacket(pkt):
    myString = "";
    for c in pkt:
        myString += "%02x" % struct.unpack("B", c)[0]
    return myString


def printpacket(pkt):
    for c in pkt:
        sys.stdout.write("%02x " % struct.unpack("B", c)[0])


def get_packed_bdaddr(bdaddr_string):
    packable_addr = []
    addr = bdaddr_string.split(':')
    addr.reverse()
    for b in addr:
        packable_addr.append(int(b, 16))
    return struct.pack("<BBBBBB", *packable_addr)


def packed_bdaddr_to_string(bdaddr_packed):
    return ':'.join('%02x' % i for i in struct.unpack("<BBBBBB", bdaddr_packed[::-1]))


def hci_enable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x01)


def hci_disable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x00)


def hci_toggle_le_scan(sock, enable):
    # hci_le_set_scan_enable(dd, 0x01, filter_dup, 1000);
    # memset(&scan_cp, 0, sizeof(scan_cp));
    # uint8_t         enable;
    #       uint8_t         filter_dup;
    #        scan_cp.enable = enable;
    #        scan_cp.filter_dup = filter_dup;
    #
    #        memset(&rq, 0, sizeof(rq));
    #        rq.ogf = OGF_LE_CTL;
    #        rq.ocf = OCF_LE_SET_SCAN_ENABLE;
    #        rq.cparam = &scan_cp;
    #        rq.clen = LE_SET_SCAN_ENABLE_CP_SIZE;
    #        rq.rparam = &status;
    #        rq.rlen = 1;

    #        if (hci_send_req(dd, &rq, to) < 0)
    #                return -1;
    cmd_pkt = struct.pack("<BB", enable, 0x00)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd_pkt)


def hci_le_set_scan_parameters(sock):
    old_filter = sock.getsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    SCAN_RANDOM = 0x01
    OWN_TYPE = SCAN_RANDOM
    SCAN_TYPE = 0x01


def parse_events(sock, loop_count=100):
    old_filter = sock.getsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    # perform a device inquiry on bluetooth device #0
    # The inquiry should last 8 * 1.28 = 10.24 seconds
    # before the inquiry is performed, bluez should flush its cache of
    # previously discovered devices
    flt = bluez.hci_filter_new()
    bluez.hci_filter_all_events(flt)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, flt)
    done = False  # Not used? -JWJ
    results = []  # Not used? -JWJ
    myFullList = []
    for i in range(0, loop_count):
        pkt = sock.recv(255)
        ptype, event, plen = struct.unpack("BBB", bytes(pkt[:3]))
        # print "--------------"
        if event == bluez.EVT_INQUIRY_RESULT_WITH_RSSI:
            i = 0
        elif event == bluez.EVT_NUM_COMP_PKTS:
            i = 0
        elif event == bluez.EVT_DISCONN_COMPLETE:
            i = 0
        elif event == LE_META_EVENT:
            subevent, = struct.unpack("B", bytes(pkt[3]))
            pkt = pkt[4:]
            if subevent == EVT_LE_CONN_COMPLETE:
                le_handle_connection_complete(pkt)
            elif subevent == EVT_LE_ADVERTISING_REPORT:
                # print "advertising report"
                num_reports = struct.unpack("B", bytes(pkt[0]))[0]
                report_pkt_offset = 0
                for i in range(0, num_reports):
                    company = returnstringpacket(pkt[report_pkt_offset + 15: report_pkt_offset + 17])

                    if (DEBUG == True):
                        print
                        "\tfullpacket: ", printpacket(pkt)

                    if (company == "3301"):
                        sensor = {}
                        #			  print "\tCompany: ",company
                        udid = returnstringpacket(pkt[report_pkt_offset + 22: report_pkt_offset - 6])
                        #			  print "\tUDID: ", udid
                        sensor["udid"] = udid

                        #			  print "\tMAJOR: ", printpacket(pkt[report_pkt_offset -6: report_pkt_offset - 4])
                        #			  print "\tMINOR: ", printpacket(pkt[report_pkt_offset -4: report_pkt_offset - 2])
                        #			  print "\tMAC address: ", packed_bdaddr_to_string(pkt[report_pkt_offset + 3:report_pkt_offset + 9])
                        mac = returnstringpacket(pkt[report_pkt_offset + 3: report_pkt_offset + 9])
                        sensor["mac"] = mac
                        #			  print "\tMAC Address string: ", returnstringpacket(pkt[report_pkt_offset + 3:report_pkt_offset + 9])
                        tempString = returnstringpacket(pkt[report_pkt_offset + 23: report_pkt_offset + 25])
                        #			  print "\tTemp: " , tempString
                        temp = float(returnnumberpacket(pkt[report_pkt_offset + 23:report_pkt_offset + 25])) / 10
                        #			  print "\tTemp: " , temp
                        sensor["temp"] = temp

                        #			  print "\tHumidity: " ,printpacket(pkt[report_pkt_offset + 25:report_pkt_offset + 27])
                        humidity = float(returnnumberpacket(pkt[report_pkt_offset + 25:report_pkt_offset + 27])) / 10
                        #			  print "\tHumidity: " ,humidity
                        sensor["humidity"] = humidity

                        dewpoint = float(returnnumberpacket(pkt[report_pkt_offset + 27:report_pkt_offset + 29])) / 10
                        #			  print "\tDewpoint: " ,dewpoint
                        sensor["dewpoint"] = dewpoint

                        nameLength = int(returnstringpacket(pkt[report_pkt_offset + 32]))
                        #			  print "\tNameLength: ",nameLength

                        name = returnstringpacket(pkt[report_pkt_offset + 33:report_pkt_offset + (33 + nameLength - 1)])
                        #			  print "\tName: %s %d " % (name.decode("hex"),nameLength)
                        sensor["name"] = name.decode("hex")

                        #			  print "\tBattery: " ,printpacket(pkt[report_pkt_offset + 18:report_pkt_offset + 19])
                        battery = float(float(returnnumberpacket(pkt[report_pkt_offset + 18]) / float(25500)) * 100)
                        #			  print "\tBattery: " ,battery
                        sensor["battery"] = battery
                        done = True

                        myFullList.append(sensor)
    #		  else:
    #			  print "\tNon blue maestro packet found"
    sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, old_filter)
    return myFullList

dev_id = 0
try:
    sock = bluez.hci_open_dev(dev_id)

except:
    print("error accessing bluetooth device...")
    sys.exit(1)

hci_le_set_scan_parameters(sock)
hci_enable_le_scan(sock)

print(parse_events(sock, 10))