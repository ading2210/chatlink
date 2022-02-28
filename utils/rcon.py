import socket, struct

#rcon protocol: wiki.vg/RCON

host, port = "127.0.0.1", 25575

#encodes a packet to raw bytes to send
def encode_packet(request_id, packet_type, payload):
    packet_pre = struct.pack("<ii", request_id, packet_type) + payload + b"\x00\x00"
    packet_final = struct.pack("<i", len(packet_pre)) + packet_pre
    return packet_final

#decodes bytes from recieved packet
def decode_packet(data):
    packet_size = struct.unpack("<i", data[:4])[0]
    request_id, packet_type = struct.unpack("<ii", data[4:12])
    payload = data[12:packet_size+2]
    return packet_size, request_id, packet_type, payload

#sends a packet to the server
def send_packet(sock, request_id, packet_type, payload):
    packet = encode_packet(request_id, packet_type, payload)
    sock.sendall(packet)

#recieves a packet from the server
def recieve_packet(sock):
    packet_encoded = sock.recv(4096)
    packet = decode_packet(packet_encoded)
    return packet

#sends a packet and returns the response
def send_recieve_packet(sock, request_id, packet_type, payload):
    send_packet(sock, request_id, packet_type, payload)
    packet = list(recieve_packet(sock))
    send_packet(sock, request_id, 100, "payload".encode())
    while True:
        latest_packet = recieve_packet(sock)
        if latest_packet[3].decode() == "Unknown request 64":
            break
        packet[3] = packet[3] + latest_packet[3]
        
    return tuple(packet)

#class to handle the RCON protocol
class RCON:
    def __init__(self, host, port, password):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10)
        self.sock.connect((host, port))
        self.password = password
        self.host = host
        self.port = port
        self.login()

    #reconnect in case of a server restart
    def reconnect(self):
        self.sock.close()
        del self.sock
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10)
        self.sock.connect((self.host, self.port))
        self.login()

    #close the connection
    def close(self):
        self.sock.close()
    
    #returns true if the login was successful
    def login(self):
        packet_type = send_recieve_packet(self.sock, 0, 3, self.password.encode())[2]
        if not packet_type == 2:
            return False
        return True

    #send a command to the server
    def send_cmd(self, command):
        returned_packet = send_recieve_packet(self.sock, 1, 2, command.encode())
        if returned_packet[2] == -1:
            self.login()
            returned_packet = send_recieve_packet(self.sock, 1, 2, command.encode())
        return returned_packet[3].decode()

if __name__ == "__main__":
    rcon = RCON(host, port, "password")
    print(rcon.send_cmd("help"))
    rcon.close()
