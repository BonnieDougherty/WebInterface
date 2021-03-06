#! /usr/bin/python

from xbee import ZigBee
import time
import serial
import Queue
from apscheduler.scheduler import Scheduler
import os.path
from Database import Database
import logging

logging.basicConfig()

BROADCAST='\x00\x00\x00\x00\x00\x00\xFF\xFF'
UNKNOWN = '\xFF\xFE'
PORT = '/dev/ttyAMA0'
BAUD_RATE = 9600
XBeeAddress = []
XBeeID = []
XBeeReference = []
XBeeFilenames = []
XBeeStatus = []
XBeeParameters = []
current_data=''

XBeeReference.append('\x00\x13\xA2\x00\x40\xAC\x17\x30')
XBeeReference.append('\x00\x13\xA2\x00\x40\xA8\xBF\x3B')
XBeeReference.append('\x00\x13\xA2\x00\x40\xA8\xC2\x37')
XBeeReference.append('\x00\x13\xA2\x00\x40\xA8\xC2\x0F')
XBeeReference.append('\x00\x13\xA2\x00\x40\xA8\xC2\x1D')
XBeeReference.append('\x00\x13\xA2\x00\x40\xAA\x19\x95')
XBeeReference.append('\x00\x13\xA2\x00\x40\xA8\xC2\x0A')
XBeeReference.append('\x00\x13\xA2\x00\x40\xAA\x19\x9D')
XBeeReference.append('\x00\x13\xA2\x00\x40\xAA\x19\xDD')
XBeeReference.append('\x00\x13\xA2\x00\x40\xAA\x1A\x7E')
XBeeReference.append('\x00\x13\xA2\x00\x40\xAA\x19\x84')
XBeeReference.append('\x00\x13\xA2\x00\x40\xAA\x1A\x59')
XBeeReference.append('\x00\x13\xA2\x00\x40\xA8\xC1\x99')

# When a packet is recieved, place it in the packets queue.
packets = Queue.Queue()
# Open serial port
ser = serial.Serial(PORT, BAUD_RATE)

def message_received(data):
    packets.put(data,block=False)

# Create API object, which spawns a new thread
xbee = ZigBee(ser,callback=message_received,escaped=True)

# Function to handle packets
def handlePacket(data):
    global current_data
    global platetimeHEX
    # Response to at packet
    if data['id'] == 'at_response':
        # Packet transmission was successful
        if data['status'] == '\x00':
            # Check to see if the address is already recorded
            for i in range(0,len(XBeeAddress)):
                if XBeeAddress[i] == data['parameter']['source_addr_long']:
                    return
            XBeeAddress.append(data['parameter']['source_addr_long'])
            check = 0
            while data['parameter']['source_addr_long'] != XBeeReference[check]:
                check = check+1
            XBeeID.append(check+1)
            XBeeStatus.append(0)
        
    if data['id'] == 'tx_status':
        # Look into re-sending packet
        pass
    
    if data['id'] == 'rx':
        # Options for data are: letter, parameters, data
        if len(data['rf_data']) == 1:
            # Recieved a letter
            x=0
            while data['source_addr_long'] != XBeeAddress[x]:
                x=x+1
            XBeeStatus[x]= data['rf_data']
            pass
        if len(data['rf_data']) == 4:
            platetimeHEX = data['rf_data']
            platetime = ord(data['rf_data'][0])*16777216 + ord(data['rf_data'][1])*65536 + ord(data['rf_data'][2])*256 + ord(data['rf_data'][3])
            print platetime
        if len(data['rf_data']) == 8 :
            # Recieved parameters
            XBeeParameters.append(int(data['rf_data'][4:8],16))
        if len(data['rf_data']) == 132:
            x=0
            while (data['source_addr_long'] != XBeeAddress[x]):
                x=x+1
            if (XBeeStatus[x]+1)%3 == 0:
                current_data=current_data+data['rf_data'][0:130]
                #current_file.write(data['rf_data'][0:130])
                #current_file.write('\n')
            else:
                current_data=current_data+data['rf_data'][0:132]
                #current_file.write(data['rf_data'][0:132])
            #current_file.close()
            XBeeStatus[x]=XBeeStatus[x]+1
            print XBeeStatus

def collect_data():
    global reads
    global current_data
    starttime = time.clock()
    for x in range(0,numReaders):
        XBeeStatus[x]=0                                                                                                                                                                              
    for x in range(0,numReaders):
        #xbee.send('tx',dest_addr_long=XBeeAddress[x],dest_addr=UNKNOWN,data=b't')
        time.sleep(1)
        current_data=''
        xbee.send('tx',dest_addr_long=XBeeAddress[x],dest_addr=UNKNOWN,data=b'D')
        start = time.clock()
        time.sleep(2)
        while XBeeStatus[x] != 12:
            if (time.clock()-start)>30:
                #xbee.send('tx',dest_addr_long=XBeeAddress[x],dest_addr=UNKNOWN,data=b'D')
                #XBeeStatus[x]=0
                #current_data=''
                #start = time.clock()
                #print ("Re-sent DATA_SEND to {0}".format(x))
                #time.sleep(2)
                print "Did not recieve data"
                XBeeStatus[x] = 12
                #xbee.send('tx',dest_addr_long=XBeeAddress[x],dest_addr=UNKNOWN,data=b't')
                current_data=1594*'0'
            if (time.clock()-starttime)>115:
                print ("Exceeded time limit")
                return
            try:
                if packets.qsize() > 0:
                    newPacket = packets.get_nowait()
                    handlePacket(newPacket)
            except KeyboardInterrupt:
                break      
        # Save to database
        db = Database(dbname)
        for res in range(0,4):
            data = current_data[res*394:res*394+394]
            well_data = ''
            for well in range(0,96):
                well_data = well_data+','+str(int(data[12+well*4:14+well*4]+data[10+well*4:12+well*4],16))
                current_time = int(data[6:8]+data[4:6]+data[2:4]+data[0:2],16)       
            db.add_data(exp_id,XBeeID[x],current_time,data[8:10],well_data) 
        db.close()

        # Save to text file
        save_path = '/media/usbhdd'
        filename = os.path.join(save_path,XBeeFilenames[x])  
        current_file = open(filename,'a')
        current_file.write(current_data)
        current_file.write('\n')
        current_file.close()
    reads = reads+1
    print ("Recieved data: {0}".format(reads))
    return

#-----Scheduler----------
SchedDataCollect = Scheduler()
#------------------------

if __name__ == '__main__':
    # Code to be executed when the script is called directly
    while packets.qsize() > 0:
        newPacket = packets.get_nowait()
    
    # Connect to database
    current = Database.get_databases()
    print current
    dbname = raw_input("Select database or create new database:")
    #print (dbname.lower() not in current)
    if (dbname.lower() not in current):
        db = Database.create_new(dbname)
    else:
        db = Database(dbname)
    name = raw_input("Name of the experiment:")
    experimenter = raw_input("Experimenter:")
    exp_id = db.add_experiment(name=name,experimenter=experimenter)

    # Send ND command - responses will create a list of addresses
    xbee.at(command=b'ND')
    numReaders = int(raw_input("How many readers?"))
    while len(XBeeID) != numReaders:
        try:
            if packets.qsize() > 0:
                newPacket = packets.get_nowait()
                handlePacket(newPacket)
        except KeyboardInterrupt:
            break
    
    # Ask for specific file names for each XBee ID:
    for x in range(0,len(XBeeID)):
        name = raw_input("Identifier {0} filename:".format(XBeeID[x]))
        XBeeFilenames.append(name)
        save_file = '/media/usbhdd/'
        file_name = os.path.join(save_file,XBeeFilenames[x])
        current_file = open(file_name,'w')
        current_file.close()
        # Add plate to database
        db.add_plate(exp_id,XBeeID[x],name)

    # Close the database
    db.close()

    # Send WAITING signal to each device
    for x in range(0,numReaders):
        xbee.send('tx',dest_addr_long=XBeeAddress[x],dest_addr=UNKNOWN,data=b'W')
        time.sleep(2)
        xbee.send('tx',dest_addr_long=XBeeAddress[x],dest_addr=UNKNOWN,data=b't')

    while len(XBeeParameters) != int(numReaders):
        try:
            if packets.qsize() > 0:
                newPacket = packets.get_nowait()
                handlePacket(newPacket)
        except KeyboardInterrupt:
            break

    # Check to make sure all the parameters are the same
    plate_delay = XBeeParameters[0]
    same = True
    for x in range(1,numReaders):
        if XBeeParameters[x] != plate_delay:
            same = False
            break

    change = 'No'
    if same == True:
        change = raw_input("Current plate delay is {0}, change parameters?".format(plate_delay))
    if change == 'YES' or same == False:
        plate_delay = int(raw_input("Plate delay (s):"))
        temp = hex(plate_delay)
        if len(temp) == 4:
            TEMPparameters = '00'+temp[2:4]
        if len(temp) == 5:
            TEMPparameters = '0'+temp[1:4]
        if len(temp) == 6:
            TEMPparameters = temp
        param = '1902' + TEMPparameters

        for x in range(0,len(XBeeID)):
            xbee.send('tx',dest_addr_long=XBeeAddress[x],dest_addr=UNKNOWN,data=b'p')
            xbee.send('tx',dest_addr_long=XBeeAddress[x],dest_addr=UNKNOWN,data=b'8')
            xbee.send('tx',dest_addr_long=XBeeAddress[x],dest_addr=UNKNOWN,data=param)

    numReads = int(raw_input("Number of readings:"))
    # Send START signal
    for x in range(0,numReaders):
        xbee.send('tx',dest_addr_long=XBeeAddress[x],dest_addr=UNKNOWN,data=b'S')
        #time.sleep(6)
    time.sleep(10)
    reads = 0
    SchedDataCollect.start()
    SchedDataCollect.add_interval_job(collect_data,seconds=plate_delay)
    collect_data()
    while reads != numReads:
        time.sleep(30)
    SchedDataCollect.shutdown()

    for x in range(0,numReaders):
        xbee.send('tx',dest_addr_long=XBeeAddress[x],dest_addr=UNKNOWN,data=b's')
    print ("Finished readings")
    # halt() must be called before closing the serial
    # port in order to ensure proper thread shutdown
    xbee.halt()
    ser.close()
