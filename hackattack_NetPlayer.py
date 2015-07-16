from hackattack_player import *
import socket, select
class NetPlayer(Player):
    sock=0
    def __init__(self, game, name, start):
        
        print "Initializing network player..."
        # List to keep track of socket descriptors
        self.CONNECTION_LIST = []
        self.RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
        self.PORT = 5000
     
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # this has no effect, why ?
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("0.0.0.0", self.PORT))
        self.server_socket.listen(10)
 
        # Add server socket to the list of readable connections
        self.CONNECTION_LIST.append(self.server_socket)
        print "Waiting for Connections"
        while (len(self.CONNECTION_LIST)<2):
            # Get the list sockets which are ready to be read through select
            self.read_sockets,self.write_sockets,self.error_sockets = select.select(self.CONNECTION_LIST,[],[])
 
            for socky in self.read_sockets:
                #New connection
                if socky == self.server_socket:
                    # Handle the case in which there is a new connection recieved through server_socket
                    self.sock, self.addr = self.server_socket.accept()
                    self.CONNECTION_LIST.append(self.sock)
                    print "Client (%s, %s) connected" % self.addr
                 
        
        # do pre stuff
        super(NetPlayer, self).__init__(game, name, start)
        # do post stuff

    def display(self, string):
        try:
            self.sock.send(message)
        except:
            # broken socket connection may be, chat client pressed ctrl+c for example
            self.CONNECTION_LIST.remove(self.sock)
	    self.sock.close()
            print "Client (%s, %s) is offline" % self.addr

    def raw_input(self, string):
        self.display(string)
        while 1:
            read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])
            for sock in self.read_sockets:
                if sock!=self.server_socket:
                    # Data recieved from client, process it
                    try:
                        #In Windows, sometimes when a TCP program closes abruptly,
                        # a "Connection reset by peer" exception will be thrown
                        data = sock.recv(RECV_BUFFER)
                        if data:
                            return data
                 
                    except:
                        print "Client (%s, %s) is offline" % self.addr
                        sock.close()
                        self.CONNECTION_LIST.remove(sock)
                        continue
