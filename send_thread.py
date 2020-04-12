from threading import Thread, RLock
from time import sleep
import socket
import sys


class SendMessage(Thread):
    def __init__(self, route_table :dict, lock :RLock, mcast_group, mcast_port, mcast_delay, mcast_ttl, addrinfo, udp_socket):

        Thread.__init__(self)
        self.route_table    = route_table
        self.lock           = lock
        self.mcast_group    = mcast_group
        self.mcast_delay    = mcast_delay
        self.mcast_ttl      = mcast_ttl
        self.addrinfo       = addrinfo
        self.udp_socket     = udp_socket
        self.mcast_port     = mcast_port
            

    def run(self):
        try:
            self.hello_sender(route_table='hello')
            
            self.lock.acquire()

        except Exception as e:
            print(f'Failed: {e}')

        finally:
            pass
            #self.lock.release()

    
    def create_socket(self):
        '''
        Cria socket UDP para o sender, define o número de hops (saltos - mcast_ttl)

        '''
        self.mcast_ttl = 2
        self.mcast_group = 'FF02::1'
        self.addrinfo = socket.getaddrinfo(self.mcast_group, None)[0]
        
        try:
            self.udp_socket = socket.socket(self.addrinfo[0], socket.SOCK_DGRAM)
            self.udp_socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, self.mcast_ttl)
            
        except Exception as sock_error:
            print(f'Failed to create socket: {sock_error}')

        return self.udp_socket

    def hello_sender(self,route_table):
        '''
        Envia hello juntamente com a tabela de roteamento (route_table)
        e fecha o socket e espera 30 segundos (mcast_delay) para voltar a repetir o processo
        '''

        self.mcast_group = 'FF02::1'
        self.mcast_port = 9999
        self.mcast_delay = 5

        while True:
            try:
                print(f'Sending multicast message to the multicast group: {self.mcast_group} ...')
                self.create_socket().sendto(self.route_table.encode(), (self.mcast_group,self.mcast_port))
                
            except (KeyboardInterrupt, SystemExit) as e:
                print('Terminating connection with Node ...')
                break
            except socket.gaierror as sock_error:
                print(f'Sending error \'gaierror\': {sock_error}')
                break
            finally:
                self.create_socket().close()
            
            sleep(self.mcast_delay)


if __name__ == "__main__":
    t = SendMessage(route_table='hello', lock=1, mcast_group=None, mcast_port=9999, mcast_delay=None, mcast_ttl=None, addrinfo=None, udp_socket=None)
    t.start()

