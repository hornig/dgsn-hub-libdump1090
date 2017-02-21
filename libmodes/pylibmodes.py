from ctypes import *
from ctypes.util import find_library
import platform
import os

def find_file_in_folder(folder, needle):
    # traverse root directory, and list directories as dirs and files as files
    list = []
    for root, dirs, files in os.walk(folder):
        path = root.split(os.sep)
        #print((len(path) - 1) * '---', os.path.basename(root))
        for file in files:
            if file.find(needle) > -1:
                list.append(root + os.path.sep + file)
                #print(root + os.path.sep + file)
    return list

def load_libmodes():
    if platform.architecture()[0] != "64bit":
        driver_files = ['libmodes.dll', 'libmodes.so']
        driver_files += ['..//libmodes.dll', '..//libmodes.so']
        driver_files += ['libmodes//libmodes.dll', 'libmodes//libmodes.so']
        driver_files += [find_library('libmodes'), find_library('libmodes')]
        driver_files += [find_file_in_folder(".", "libmodes.dll")[0], find_file_in_folder(".", "libmodes.so")[0]]
    else:
        driver_files = ['libmodes64.dll', 'libmodes.so']
        driver_files += ['..//libmodes64.dll', '..//libmodes.so']
        driver_files += ['libmodes//libmodes64.dll', 'libmodes//libmodes.so']
        driver_files += [find_file_in_folder(".", "libmodes64.dll")[0], find_file_in_folder(".", "libmodes.so")[0]]

    dll = None

    for driver in driver_files:
        try:
            dll = CDLL(driver)
            break
        except:
            pass
    else:
        raise ImportError('Error loading libmodes. Make sure libmodes '\
                          '(and all of its dependencies) are in your path')

    return dll

libModeS = load_libmodes()


class modesMessage(Structure):
    pass

modesMessage._fields_ = [("msg", c_char*14),
                        ("msgpos", c_int),
                        ("msgbits", c_int),
                        ("msgtype", c_int),
                        ("crcok", c_int),
                        ("crc", c_uint),
                        ("correctedbits", c_int),
                        ("corrected", c_char*2),
                        ("addr", c_uint),
                        ("phase_corrected", c_int),
                        ("timestampMsg", c_uint64),
                        ("remote", c_uint),
                        ("signalLevel", c_char),
                        ("ca", c_int),
                        ("iid", c_int),
                        ("metype", c_int),
                        ("mesub", c_int),
                        ("heading", c_int),
                        ("raw_latitude", c_int),
                        ("raw_longitude", c_int),
                        ("fLat", c_double),
                        ("fLon", c_double),
                        ("flight", c_char*16),                        
                        ("ew_velocity", c_int),
                        ("ns_velocity", c_int),
                        ("vert_rate", c_int),
                        ("velocity", c_int),
                        ("fs", c_int),
                        ("modeA", c_int),
                        ("altitude", c_int),                        
                        ("unit", c_int),
                        ("bFlags", c_int),
                        ("next", POINTER(modesMessage))]

# void modesInit();
f = libModeS.modesInit
f.restype, f.argtypes = None, None

# void setAggressiveFixCRC();
f = libModeS.setAggressiveFixCRC
f.restype, f.argtypes = None, None

# void setFixCRC();
f = libModeS.setFixCRC
f.restype, f.argtypes = None, None

# void setPhaseEnhance();
f = libModeS.setPhaseEnhance
f.restype, f.argtypes = None, None

# struct modesMessage *processData(unsigned char *buf);
f = libModeS.processData
f.restype, f.argtypes = POINTER(modesMessage), [c_char_p]

__all__ = ['libModeS', 'modesMessage']
