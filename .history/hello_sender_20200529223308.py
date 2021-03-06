from threading import Thread, RLock
from time import sleep
from json import dumps
import os
from uuid import uuid4
from signal import SIGUSR1
import struct
import socket

class HelloSender(Thread):
    def __init__(self, route_table, lock, hello_interval, localhost, ttl, mcast_group, mcast_port):

        Thread.__init__(self)
        self.route_table    = route_table
        self.lock           = lock
        self.hello_interval = hello_interval
        self.ttl            = ttl
        self.localhost      = localhost
        self.mcast_group    = mcast_group
        self.mcast_port     = mcast_port

    def run(self):
        while True:
            try:
                self.lock.acquire()
                self.hello_sender()

            except Exception as e:
                print('Failed: {}'.format(e.with_traceback()))

            finally:
                self.lock.release()
                sleep(self.hello_interval)



    def create_socket(self):

        try:
            # Criar o socket udp do client
            client_sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            client_sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, self.ttl)

            return client_sock

        except Exception as sock_error:
            print('Failed to create socket: {}'.format(sock_error))

    def hello_sender(self):

        '''
        Envia Messagem do tipo "HELLO" juntamente com a tabela de roteamento (route_table)
        e fecha o socket
        '''
        try:
            client_sock = self.create_socket()

            # Hello message to be sent
            self.msg = {
                "type": "HELLO",
                "source": self.localhost
            }

            for keys, values in self.route_table.items():
                if values['next_hop'] == None:
                    self.msg[keys] = values['timestamp']

            client_sock.sendto(dumps(self.msg).encode('utf-8'), (self.mcast_group,self.mcast_port))

        except socket.gaierror as socket_error:
            print('Sending error: {}'.format(socket_error))

        finally:
            client_sock.close()

    def route_request(self, target, msg):
        client_sock = self.create_socket()
        try:
            self.id = uuid4()
            self.pid = ogetpid()

            self.msg = {
                "type": "ROUTE_REQUEST",
                "dest": target,
                "path": [""],
                "pid": self.pid,
                "ttl": self.ttl,
                "id": f'{self.id}'
            }
            print(self.msg)

            print('Route Request ...')
            client_sock.sendto(dumps(self.msg).encode('utf-8'), (self.mcast_group,self.mcast_port))

        except socket.gaierror as socket_error:
            print('Sending error: {}'.format(socket_error))

        finally:
            client_sock.close()

    def route_reply(self):
        client_sock = self.create_socket()
        self.pid = os.getpid()

        try:
            self.msg = {
            "type": "ROUTE_REPLY",
            "dest": "target",
            "path": [""],
            "pid": self.pid,
            "ttl": self.ttl
            }
            print(self.msg)

            print('Route Request ...')
            client_sock.sendto(dumps(self.msg).encode('utf-8'), (self.mcast_group,self.mcast_port))

        except socket.gaierror as socket_error:
            print('Sending error: {}'.format(socket_error))

        finally:
            client_sock.close()

"""
rota = SendMessage(route_table=1, lock=1, hello_interval=2, ttl=4, mcast_group="FF02::1", mcast_port=9999)
rota.route_request('localhost', 'route')
print("--------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
rota.route_reply()
"""
