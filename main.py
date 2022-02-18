import os
from ymodem import YMODEM
from time import sleep
import time
import threading
import serial.tools.list_ports

import RPi.GPIO as GPIO

PowerLPin = 2
PowerRPin = 3
COUNT = 0

#####################################################################
#UI function
#####################################################################

 
def upgrade_callback(total_packets,file_size,file_name):
    tt = total_packets
    fs = file_size
    fn = file_name

#####################################################################
#ymodem_send
#####################################################################
def ymodem_send(file):
    global ymodem_sender
    try:
        file_stream = open(file, 'rb')
    except IOError as e:
        raise Exception("Open file fail!")
    file_name = os.path.basename(file)
    file_size = os.path.getsize(file)
     
    try:
        print("start sending")
        ymodem_sender.send(file_stream, file_name,file_size,callback=upgrade_callback)
    except Exception as e:
        file_stream.close()
        raise
    file_stream.close()


#####################################################################
#serial sender
#####################################################################
def sender_getc(size):
    return ser.read(size) or None
 
def sender_putc(data):
    ser.write(data)




ymodem_sender = YMODEM(sender_getc, sender_putc)
ser = serial.Serial(bytesize=8, parity='N', stopbits=1, timeout=10, write_timeout=10)
filelink = ""
#####################################################################
#main
#####################################################################
def read_bin():
    global filelink
    #script_dir = os.path.dirname(__file__)
    script_dir = os.getcwd()
    for file in os.listdir(script_dir+"/mydir"):
        if file.endswith(".bin"):
            print(os.path.join("/mydir", file))
            filelink = script_dir+"/mydir/"+file
            print(filelink)
            file_size = os.path.getsize(filelink)
            print(file_size)
            if file_size > 2*1024*1024:   #2*1024*1024
                print("file size is big")
            #ymodem_send(filelink)


        
#####################################################################
#main upgrade
#####################################################################
def do_upgrade(n):
    global ser
    global filelink
    global COUNT
    n=n+1
    COUNT = COUNT + 1

    read_bin()

    while COUNT<n:
        print("COUNT="+str(COUNT))
        prepare_upgrade_2()
        time.sleep(4)
        wd_str = ser.read(ser.inWaiting()).decode("utf-8")
        print(wd_str)
        ser.flushOutput()           #flash TX
        ser.flushInput()            #flash RX
        print("SEND X")
        ser.write("X".encode("utf-8"))      #to start the system
        time.sleep(4)
        wd_str = ser.read(ser.inWaiting()).decode("utf-8")
        print(wd_str)
        ser.flushOutput()           #flash TX
        ser.flushInput()            #flash RX
        #time.sleep(2)
        wd_str = ser.read(ser.inWaiting()).decode("utf-8")
        print(wd_str)
            #ser.write("upgrade -u\r".encode("utf-8"))
        print("START BURN")
        time.sleep(2)
        wd_str = ser.read(ser.inWaiting()).decode("utf-8")
        print(wd_str)
        ser.flushOutput()           #flash TX
        ser.flushInput()            #flash RX
      #  while True:
      ##      ch_str = ser.read(ser.inWaiting()).decode("utf-8")       #4
       #     if(ch_str):
      #          print(ch_str)
       #         if ch_str == "C":                        #CCCC
      #              break
                    
        print("START YMODEM send")    
        ymodem_send(filelink)           #do ymodem
        print("YMODEM DONE")
        time.sleep(2)
        wd_str = ser.read(ser.inWaiting()).decode("utf-8")
            #wd_str = ser.readall().decode("utf-8")
        print(wd_str)
        print("YMODEM DONE")
        print("SEND Z")
        ser.write("Z".encode("utf-8"))      #to start the system
        time.sleep(2)
        wd_str = ser.read(ser.inWaiting()).decode("utf-8")
        print(wd_str)
        time.sleep(2)
        COUNT = COUNT+1
        print("COUNT"+str(COUNT))






#####################################################################
#prepare_upgrade_2
#####################################################################
def prepare_upgrade_2():
    global ser
    #ser.flushOutput()           #flash TX
    #ser.flushInput()            #flash RX
    print("START INTO MODE and ACSII command")
    wd_str = ser.read(ser.inWaiting()).decode("utf-8")
    print(wd_str)
    time.sleep(1)
    ser.write("\r\n".encode("utf-8"))    
    time.sleep(1)
    ser.write(":0160000000\r\n".encode("utf-8"))  #get into systemm mode
    time.sleep(1)
    wd_str = ser.read(ser.inWaiting()).decode("utf-8")
    print(wd_str)  
    ser.write(":0192000000\r\n".encode("utf-8"))  #bypass mode
    time.sleep(1)
    wd_str = ser.read(ser.inWaiting()).decode("utf-8")
    print(wd_str)
    while(wd_str):
        time.sleep(1)
        wd_str = ser.read(ser.inWaiting()).decode("utf-8")
        print(wd_str)
        
    #ser.write("X".encode("utf-8"))  #write \r    
    #ser.write("\r".encode("utf-8"))  #write \r
    #ret_str = ser.read(1024).decode("utf-8")
    #print(ret_str)
    return 0


def pypass_sensor(a):
    global COUNT
    COUNT = a
    for x in range(a):

        
        print("pypass sensor="+str(x+1))
        ser.write("a".encode("utf-8"))  #bypass mode        
        time.sleep(1)
        ser.write("Z".encode("utf-8"))  #bypass mode
        time.sleep(2)
        wd_str = ser.read(ser.inWaiting()).decode("utf-8")
        print(wd_str)         
        prepare_upgrade_2()
#####################################################################
#serial reconnect
#####################################################################
 
def connect():
    global ser
    try:
        ser.port = "/dev/ttyS0"   #"COM3"
        ser.baudrate = 9600 #int(baud_rate)
        #ser.bytesize = serial.SEVENBITS
        #ser.parity = serial.PARITY_ODD
        #ser.stopbits = serial.STOPBITS_TWO
        if ser.is_open == False:
            ser.open()
            print(ser.port)
            print(ser.baudrate)
            print("porte open done")
        else:
            ser.close()
    except Exception as e:
        print(e)
        return
    #ser.open()

#####################################################################
#buttonn Disconnect
#####################################################################

        
def disconnect():
    global ser

    if ser.is_open == False:
      print("ERROR ser")
    else:
        try:
            ser.close()
        except Exception as e:
            print("ERROR ser")
            return

def IO_SET():
    print("reset sensor")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PowerLPin,GPIO.OUT)
    GPIO.setup(PowerRPin,GPIO.OUT)
    GPIO.output(PowerLPin,GPIO.LOW)
    GPIO.output(PowerRPin,GPIO.LOW)    
    time.sleep(1)
    GPIO.output(PowerLPin,GPIO.HIGH)
    GPIO.output(PowerRPin,GPIO.HIGH) 


connect()
IO_SET()
#prepare_upgrade_2()
pypass_sensor(0)
#COUNT =19
do_upgrade(50)

