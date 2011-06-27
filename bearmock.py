# Uniden Bearcat serial emulator
# Use it on windows with com0com
# -- Gabriel Tremblay initnull hat gmail dot com
#################################################

from time import sleep

__author__ = 'initnull@Groupies'

from serial import Serial
from serial.serialutil import SerialException, portNotOpenError

__MODEL = 'BCD296D'
__PORT = 'COM12'
__SPEED = 57600
__TIMEOUT = 0 # non-blocking, return on read
__READ_SLEEP_SECS = 0
__OUT = 'decoded.s19'

__ACTIONS = {
    '\r' : 'OK\r', # Empty, just reply
    '*SUM\r' : '10000\r',
    '*SPD 4\r' : 'SPEED ' + str(__SPEED) +  ' bps\r',
    '*SPD 5\r' : 'SPEED ' + str(__SPEED) +  ' bps\r',
    '*PGL 11000000000\r' : 'OK\r',
    '*PGL 1000000000000000000\r' : 'OK\r',
    '*ULE\r' : 'OK\r',
    '*PRG\r' : 'OK\r',
    '*MDL\r' : __MODEL + '\r',
    '*FDP\r' : 'FDP 3.\r',
    '*REG\r' : 'OK\r',
    '*SCB 1\r' : 'SCB 1\r',
    '*APP\r' : 'OK\r',
}


# Main loop
if __name__ == "__main__":
    try:
        port = Serial(__PORT, __SPEED, timeout=__TIMEOUT)
    except SerialException:
        print "Error: Port already in use."
        exit()

    outfile = open(__OUT, 'wb')

    print "Reading port..."
    readbuf = ''
    while True:
        try:
            byte = port.read()
            if len(byte) > 0:
                num = int(byte.encode('hex'), 16)
                readbuf = ''.join([readbuf, chr(num)])
                if num == 13:
                    if readbuf[0:2] == 'S8':
                        readbuf = readbuf.replace('\x0d', '\x0d\x0a')
                        outfile.write(readbuf)
                        outfile.close()
                        print "Done"
                        exit()
                    elif readbuf[0:2] == 'S0' or readbuf[0:2] == 'S2':
                        readbuf = readbuf.replace('\x0d', '\x0d\x0a')
                        outfile.write(readbuf)
                        port.write('\r')
                    else:
                        print "Received command: ",
                        print readbuf.strip(' ')

                        # execute action based on query
                        action = __ACTIONS.get(readbuf.strip(''))
                        if not action:
                            print "No corresponding action found"
                        else:
                            print "Sending: " + action + "\n"
                            port.write(__ACTIONS.get(readbuf.strip(' ')))

                    port.flush()
                    readbuf = ''
        except portNotOpenError:
            print "Error: Port was closed"
            exit()

        sleep(__READ_SLEEP_SECS)

    outfile.close()
