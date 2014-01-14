#! /usr/bin/python

from xbee import ZigBee
import time
import serial
import Queue
from apscheduler.scheduler import Scheduler
import os.path

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
XBeeReference.append('\x00\x13\xA2\x00\x40\xAC\x17\x30')
XBeeReference.append('\x00\x13\xA2\x00\x40\xA8\xBF\x3B')
XBeeReference.append('\x00\x13\xA2\x00\x40\xA8\xC2\x37')
XBeeReference.append('\x00\x13\xA2\x00\x40\xA8\xC2\x0F')
XBeeReference.append('\x00\x13\xA2\x00\x40\xA8\xC2\x1D')
XBeeReference.append('\x00\x13\xA2\x00\x40\xAA\x19\x95')
XBeeReference.append('\x00\x13\xA2\x00\x40\xA8\xC2\x0A')
XBeeReference.append('\x00\x13\xA2\x00\x40\xAA\x19\x9D')
XBeeReference.append('\x00\x13\xA2\x00\x40\xAA\x19\xDD')
XBeeReference.append('\x00\x13\xA2\x00\x40\xAA\x1A\x7B')
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
    if data['id'] == 'at_response':
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
        if len(data['rf_data']) == 8 :
            # Recieved parameters
            XBeeParameters.append(int(data['rf_data'][4:8],16))
        if len(data['rf_data']) == 132:
            x=0
            while (data['source_addr_long'] != XBeeAddress[x]):
                x=x+1
            
            
            save_path = '/media/usbhdd/'
            filename = os.path.join(save_path,XBeeFilenames[x])
            current_file = open(filename,'a')
            if (XBeeStatus[x]+1)%3 == 0:
                current_file.write(data['rf_data'][0:130])
                current_file.write('\n')
            else:
                current_file.write(data['rf_data'][0:132])
            current_file.close()
            XBeeStatus[x]=XBeeStatus[x]+1

def collect_data():
    global reads
    current = []
    XBeeStart = []
    for x in range(0,numReaders):
        XBeeStatus[x]=0                                                                                                                                                                              
    for x in range(0,numReaders):
        xbee.send('tx',dest_addr_long=XBeeAddress[x],dest_addr=UNKNOWN,data=b'D')
        start = time.clock()
        time.sleep(2)
        while XBeeStatus[x] != 12:
            if (time.clock()-start)>30:
                xbee.send('tx',dest_addr_long=XBeeAddress[x],dest_addr=UNKNOWN,data=b'D')
                start = time.clock()
                print ("Re-sent DATA_SEND to {0}".format(x))
                time.sleep(2)
            try:
                if packets.qsize() > 0:
                    newPacket = packets.get_nowait()
                    handlePacket(newPacket)
                    print XBeeStatus
            except KeyboardInterrupt:
                    break
    """
    for x in range(0,3):
        xbee.send('tx',dest_addr_long=XBeeAddress[x],dest_addr=UNKNOWN,data=b'D')
        print("Sent DATA_SEND to {0}".format(x))
        current.append(x)
        XBeeStart.append(time.clock())
    time.sleep(2)
    print ("Current: {0}".format(current))
    while sum(XBeeStatus) != (36*numReaders):
        while x != numReaders-1:
            while XBeeStatus[current[0]] != 36 and XBeeStatus[current[1]] != 36 and XBeeStatus[current[2]] != 36:
	        try:
                    while packets.qsize() > 0:
                        newPacket = packets.get_nowait()
                        handlePacket(newPacket)
                        print XBeeStatus
                except KeyboardInterrupt:
                    break
            print("Sent DATA_SEND to {0}".format(x))
            if(XBeeStatus[current[0]] == 36) and x != numReaders-1:
                x = x+1
                xbee.send('tx',dest_addr_long=XBeeAddress[x],dest_addr=UNKNOWN,data=b'D')
                XBeeStart[0] = time.clock()
                time.sleep(1)
                current[0] = x
            if(XBeeStatus[current[1]] == 36) and x != numReaders-1:
                x=x+1
                xbee.send('tx',dest_addr_long=XBeeAddress[x],dest_addr=UNKNOWN,data=b'D')
                XBeeStart[1] = time.clock()
                time.sleep(1)
                current[1] = x
            if(XBeeStatus[current[2]] == 36) and x != numReaders-1:
                x=x+1
                xbee.send('tx',dest_addr_long=XBeeAddress[x],dest_addr=UNKNOWN,data=b'D')
                XBeeStart[2] = time.clock()
                time.sleep(1)
                current[2] = x
            print ("Current: {0}".format(current))

        # Sent SEND_DATA signal to all plate_readers, waiting for data
        time.sleep(5)
        while packets.qsize() > 0:
            newPacket = packets.get_nowait()
            handlePacket(newPacket)
            print XBeeStatus
        
        # Check to see if one wasn't fully recieved
        for y in range(0,3): 
            if XBeeStatus[current[y]] != 36 and (time.clock()-XBeeStart[y]) > 15:
                print "Entered time check"
                XBeeStatus[y] = 0
                xbee.send('tx',dest_addr_long=XBeeAddress[y],dest_addr=UNKNOWN,data=b'D')
                print ("Re-sent DATA_SEND to {0}".format(y))
                XBeeStart[y]=time.clock()
                time.sleep(5)
    """
        
    reads = reads+1
    print ("Recieved data: {0}".format(reads))

#-----Scheduler----------
SchedDataCollect = Scheduler()
#------------------------

if __name__ == '__main__':
    # Code to be executed when the script is called directly
    while packets.qsize() > 0:
        newPacket = packets.get_nowait()
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
    
    # Open the database file
    db = Database()
    
    # Create new entry in the experiments table 
    name = raw_input("Name of the experiment:")
    experimenter = raw_input("Experimenter")
    exp_id = db.add_experiment(name=name,experimenter=experimenter)
    
    # Create entries in the plate table for each plate in the experiment
    for x in range(0,len(XBeeID)):
        name = raw_input("Identifier {0} filename:".format(XBeeID[x]))
        db.add_plate(exp_id,XBeeID[x],name)
        
    # Send WAITING signal to each device
    for x in range(0,numReaders):
        xbee.send('tx',dest_addr_long=XBeeAddress[x],dest_addr=UNKNOWN,data=b'W')

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
