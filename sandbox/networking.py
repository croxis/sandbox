# ## Python 3 look ahead imports ###
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import socket

from direct.directnotify.DirectNotify import DirectNotify

from .systems import EntitySystem

__author__ = 'croxis'

log = DirectNotify().newCategory("SandBox-Networking")


class UDPNetworkSystem(EntitySystem):
    def init(self, address='127.0.0.1', port=1999, upper_port=2014,
             compress=False):
        """

        :param address:
        :param port:
        :param upper_port:
        :param compress:
        """
        log.debug("Initiating Network System on port " + str(port))

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        connected = False
        while not connected:
            try:
                self.udp_socket.bind((address, port))
                connected = True
                log.info("Socket bound to: " + str((address, port)))
                print("Socket bound to: " + str((address, port)))
            except socket.error:
                port += 1
                if port is upper_port:
                    log.warning("No sockets open in range.")
                    return

        self.udp_socket.setblocking(0)

        self.lastAck = {}  # {NetAddress: time}
        self.activeConnections = {}  # {NetAddress : PlayerComponent}

        self.start_polling()
        self.init2()

    def init2(self):
        """This function is overridden for initialization instead of __init__."""

    def start_polling(self):
        #taskMgr.add(self.tskReaderPolling, "serverListenTask", -40)
        base.taskMgr.doMethodLater(10, self.active_check, "active_check")

    def begin(self):
        try:
            data, addr = self.udp_socket.recvfrom(1024)
        except:
            return
            #msgID, remotePacketCount, ack, acks, hashID, serialized = self.unpack_packet(data)
        split = unpack_packet(data)
        self.process_packet(split[0], split[1], split[2], split[3], split[4],
                            split[5], addr)
        self.lastAck[addr] = datetime.datetime.now()

    def process_packet(self, msgID, remotePacketCount, ack, acks, hashID,
                       serialized, address):
        """Override to process data"""
        log.error(u"{0} has no process function.".format(unicode(self)))
        raise NotImplementedError

    def active_check(self, task):
        """Checks for last ack from all known active connections.
        playerDisconnected, address message fires if a player disconnects"""
        return task.again
        for address, lastTime in self.lastAck.items():
            if (datetime.datetime.now() - lastTime).seconds > 30:
                #print self.activeConnections
                self.activeConnections[address].address = ('', 0)
                del self.activeConnections[address]
                del self.lastAck[address]
                send('playerDisconnected', [address])
                #TODO: Disconnect
        return task.again

    def send_data(self, datagram, address):
        if len(datagram) > 512:
            log.error(
                "Datagram too large (" + str(len(datagram)) + "): " + datagram)
            raise Exception
            return
        self.udp_socket.sendto(datagram, address)


def unpack_packet(datagram):
    try:
        split = datagram.split(',', 5)
        return int(split[0]), int(split[1]), int(split[2]), int(split[3]), int(
            split[4]), split[5]
    except:
        raise errors.InvalidPacket(datagram)


def generate_generic_packet(key, packetCount=0):
    datagram = str(key) + ',' + '0,0,0,0,'
    return datagram


def generate_packet(key, message, packetCount=0):
    datagram = generate_generic_packet(key,
                                       packetCount=0) + message.to_bytes_packed()
    return datagram