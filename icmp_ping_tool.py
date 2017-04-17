#!/usr/bin/python
# encoding: utf-8
# -*- coding: utf8 -*-
"""
Created by PyCharm.
File:               LinuxBashShellScriptForOps:odbp_database.py.py
User:               Yinweihai
Create Date:        2017/4/17
Create Time:        17:30
"""
import os
import argparse
import socket
import struct
import select
import time
import msg_send

ICMP_ECHO_REQUEST = 8  # Platform specific
DEFAULT_TIMEOUT = 2
DEFAULT_COUNT = 1


class Pinger(object):
    def __init__(self, target_host, count=DEFAULT_COUNT, timeout=DEFAULT_TIMEOUT):
        self.target_host = "118.188.0.80"
        self.count = count
        self.timeout = timeout

    def do_checksum(self, source_bytes):
        sum = 0
        curnum = int.from_bytes(source_bytes, byteorder="big")
        while curnum:
            tmp = curnum & 0xffff
            sum += tmp
            curnum = curnum >> 16
        sum = (sum >> 16) + (sum & 0xffff)
        sum = sum + (sum >> 16)
        answer = ~sum
        answer = answer & 0xffff
        return answer

    def receive_pong(self, sock, ID, timeout):
        time_remaining = timeout
        while True:
            start_time = time.time()
            readable = select.select([sock], [], [], time_remaining)
            time_spent = (time.time() - start_time)
            if readable[0] == []:  # Timeout
                return
            time_received = time.time()
            recv_packet, addr = sock.recvfrom(1024)
            icmp_header = recv_packet[20:28]
            type, code, checksum, packet_ID, sequence = struct.unpack(
                "bbHHh", icmp_header
            )
            if packet_ID == ID:
                bytes_In_double = struct.calcsize("d")
                time_sent = struct.unpack("d", recv_packet[28:28 + bytes_In_double])[0]
                return time_received - time_sent

            time_remaining = time_remaining - time_spent
            if time_remaining <= 0:
                return

    def send_ping(self, sock, ID):
        target_addr = socket.gethostbyname(self.target_host)
        my_checksum = 0
        header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)
        bytes_In_double = struct.calcsize("d")
        data = struct.pack("d", time.time())
        my_checksum = self.do_checksum(header + data)
        header = struct.pack(
            "bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1
        )
        packet = header + data
        sock.sendto(packet, (target_addr, 1))

    def ping_once(self):
        icmp = socket.getprotobyname("icmp")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        except socket.error as msg:
            if msg.errno == 1:
                msg += "ICMP messages can only be sent from root user processes"
                raise socket.error(msg)
        except Exception as e:
            print("Exception: %s" % (e))
        my_ID = os.getpid() & 0xFFFF
        self.send_ping(sock, my_ID)
        delay = self.receive_pong(sock, my_ID, self.timeout)
        sock.close()
        return delay

    def ping(self):
        """
        Run the ping process
        """
        for i in range(self.count):
            print("Ping to %s..." % self.target_host)
            try:
                delay = self.ping_once()
            except socket.gaierror as e:
                print("Ping failed. (socket error: '%s')" % e[1])
                break

            if delay == None:
                msg = msg_send.WeiXinSendMsgClass()
                msg.send("Ping %s failed. (timeout within %ssec.)" % (self.target_host, self.timeout))
            else:
                delay = delay * 1000
                print("Get pong in %0.4fms" % delay)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Python ping')
    parser.add_argument('--target-host', action="store", dest="target_host", required=False)
    given_args = parser.parse_args()
    target_host = given_args.target_host
    pinger = Pinger(target_host=target_host)
    pinger.ping()
