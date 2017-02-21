from ctypes import *
from time import gmtime
from libmodes import *
from pprint import pprint
import sys
import json
#from bitstring import *
#except ImportError: from .libmodes import libModeS, modesMessage
import os

line = 0

class ModeSDetectorMessage():
    """
    Class member variables
    """
    msg = None
    msgpos = None
    msgposline = None
    msgbits = None
    msgtype = None
    crcok = None
    crc = None
    correctedbits     = None
    corrected         = None
    addr             = None
    phase_corrected = None
    timestampMsg    = None
    remote             = None
    signalLevel     = None
    capability         = None
    iid     = None
    metype     = None
    mesub     = None
    heading = None
    raw_latitude     = None
    raw_longitude     = None
    fLat     = None
    fLon     = None
    flight     = None
    ew_velocity = None
    ns_velocity = None
    vert_rate     = None
    velocity     = None
    fs             = None
    modeA         = None
    altitude     = None
    unit     = None
    bFlags     = None

    """
    Initializes the object with a mode_s message struct
    TODO: support for bflags
    """
    def __init__(self, modesMessage):
        if sys.version_info[0] >= 3:
            self.msg     = "".join("{:02x}".format(c) for c in modesMessage.msg)
        else:
            self.msg     = "".join("{:02x}".format(ord(c)) for c in modesMessage.msg)

        # this msg needs to be sanitized...
        if modesMessage.msgbits == 56:
            self.msg     = self.msg[:14]
        self.msgpos        = modesMessage.msgpos + line
        #self.msgposline = 0
        self.msgbits     = modesMessage.msgbits
        self.msgtype     = modesMessage.msgtype
        self.crcok         = False if modesMessage == 0 else True
        self.crc         = "{:06x}".format(modesMessage.crc)
        self.correctedbits = modesMessage.correctedbits
        self.corrected     = modesMessage.corrected.decode()
        self.addr         = "{:06x}".format(modesMessage.addr)
        self.phase_corrected = False if modesMessage.phase_corrected == 0 else True
        # note: this timestamp is left out at the moment
        self.timestampMsg     = gmtime()
        self.remote         = modesMessage.remote
        self.signalLevel    = ord(modesMessage.signalLevel)
        self.capability        = modesMessage.ca
        self.iid            = modesMessage.iid
        self.metype            = modesMessage.metype
        self.mesub            = modesMessage.mesub
        self.heading        = modesMessage.heading
        self.raw_latitude    = modesMessage.raw_latitude
        self.raw_longitude    = modesMessage.raw_longitude
        self.fLat            = modesMessage.fLat
        self.fLon            = modesMessage.fLon
        self.flight            = modesMessage.flight.decode()
        self.ew_velocity    = modesMessage.ew_velocity
        self.ns_velocity    = modesMessage.ns_velocity
        self.vert_rate        = modesMessage.vert_rate
        self.velocity         = modesMessage.velocity
        self.fs             = modesMessage.fs
        self.modeA             = modesMessage.modeA
        self.altitude     = modesMessage.altitude
        self.unit         = 'feet' if modesMessage.unit == 0 else 'meter'
        self.bFlags        = modesMessage.bFlags



class ModeSDetector(object):

    #ADSB_FREQ = 1090000000
    #ADSB_RATE = 2000000
    ADSB_BUF_SIZE = 4*16*16384 # 1MB

    messages = []

    def __init__(self, device_index=0):
        self.device_index = device_index
        libModeS.modesInit()
        libModeS.setPhaseEnhance()
        libModeS.setAggressiveFixCRC()


    def readFromFile(self, filename):
        with open(filename,'rb') as f:
            while True:
                data = f.read(self.ADSB_BUF_SIZE)

                if not data:
                    break
                else:
                    buff = create_string_buffer(data)
                    mm = libModeS.processData(buff)
                    self.readDataToBuffer(mm)

    def readFromChunk(self, data):
        buff = create_string_buffer(data)
        mm = libModeS.processData(buff)
        self.readDataToBuffer(mm)

    def readDataToBuffer(self,mm):
        while mm:
            message = ModeSDetectorMessage(mm.contents)
            self.messages.append(message)
            mm = mm.contents.next

    def printMessages(self, filename):
        adsb_msg = []
        for message in self.messages:
            adsb_msg.append(vars(message))
        adsb = {"adsb" : adsb_msg}

        # Writing JSON data
        with open(filename, 'w') as f:
            json.dump(adsb, f, indent=2)

        print("adsb messages found =", len(adsb_msg))


def run(path_storing, input_filename):
    #modes = ModeSDetector()
    #modes.readFromFile(filename)
    #modes.printMessages()

    global line
    line = 0
    ADSB_BUF_SIZE = 4*16*16384

    with open(input_filename,'rb') as f:
            while True:
                data = f.read(ADSB_BUF_SIZE)

                if not data:
                    break
                else:
                    if len(data) >= ADSB_BUF_SIZE:
                        modes = ModeSDetector()
                        ModeSDetector.ADSB_BUF_SIZE = ADSB_BUF_SIZE
                        #modes.__init__(0)
                        modes.readFromChunk(data)
                        #del modes
                        line = line + int(len(data)/2.0)

    filename = input_filename.split(".")[0].split(os.path.sep)[-1]
    if input_filename.find("/") > -1:
        filename = input_filename.split(".")[0].split("/")[-1]

    modes.printMessages(path_storing + filename + ".json")
    ModeSDetector.messages = []

if __name__ == '__main__':
    #run("output.bin")
    run("", "c42336acbd699af80058bd4551ddde17b98fb9eb1c23116b08f48750_f1090000000_d0_t1487623295.dat")