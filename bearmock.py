# Uniden Bearcat serial emulator
#
# Mocks a BCD296D AND/OR a BCi96D card.
# Tested with 3.15 and 3.60 update (should be enough ;))
#
# Use it on windows with com0com (Virtual port class COMX->COMY) Default opts
#
# -- Gabriel Tremblay gabriel hat subatomicsecurity dot com
#################################################


from time import sleep

__author__ = 'initnull@Groupies'

from serial import Serial
from serial.serialutil import SerialException, portNotOpenError

__MODEL = 'BCD296D'
__PORT = 'COM11'
__SPEED = 115200 # don't touch this, com0com will adapt.
__TIMEOUT = 0  # non-blocking, return on read
__READ_SLEEP_SECS = 0
__OUT = 'decoded.s19'


__ACTIONS = {
    '\r': 'UNKNOWN COMMAND\r',  # Empty, just reply
    '*SUM\r': 'CHECKSUM= DEADH\r',  # Fake _outdated_ checksum
    '*SPD 1\r': 'SPEED 9600 bps\r',
    '*SPD 2\r': 'SPEED 19200 bps\r',
    '*SPD 3\r': 'SPEED 38400 bps\r',
    '*SPD 4\r': 'SPEED 57600 bps\r',
    '*SPD 5\r': 'SPEED 115200 bps\r',
    '*PGL 11000000000\r': 'OK\r',
    '*PGL 1000000000000000000\r': 'OK\r',
    '*PGL 1100000\r': 'OK\r',
    '*ULE\r': 'OK\r',
    '*PRG\r': 'OK\r',
    '*MDL\r': __MODEL + '\r',
    '*FDP\r': 'FDP 3.\r',
    '*REG\r': 'R 1\r',
    '*APP\r': 'Version 3.00.00\r',
    '*VER\r': 'Version 3.00.00\r',
    '*SCB 1\r': 'SCB 1\r',
    '*RTS F\r': 'RTS OFF\r',
    '*MOD 1\r': 'MODE 1\r',
    '*WWS N\r': 'WWS 0\r',
    '*SUM 1 0\r': 'CHECKSUM= C68FH\r',
    '*SUM 6 0\r': 'CHECKSUM= DEADH\r',
}


# Main loop
if __name__ == "__main__":
    try:
        port = Serial(__PORT, __SPEED, timeout=__TIMEOUT, bytesize=8, parity='N', stopbits=1)
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
                #print str(num) + ' (' + chr(num) + ')'
                readbuf = ''.join([readbuf, chr(num)])
                if num == 13:  # got a \r == end of line
                    if readbuf[0:2] == 'S8':
                        print "End of firmware (updater will crash ;)"
                        readbuf = readbuf.replace('\x0d', '\x0d\x0a')
                        outfile.write(readbuf)
                        outfile.close()
                        exit()
                    elif readbuf[0:2] == 'S0' or readbuf[0:2] == 'S2':
                        readbuf = readbuf.replace('\x0d', '\x0d\x0a')
                        outfile.write(readbuf)
                    else:
                        print "Received command: ",
                        print readbuf

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
