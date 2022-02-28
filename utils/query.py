import socket, struct

class Query:
    def __init__(self, address):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(2)
        self.address = address

    #sends a packet
    def send_packet(self, packet):
        self.sock.sendto(packet, self.address)

    #recieves a packet and returns the raw data
    def recieve_packet(self):
        data, server = self.sock.recvfrom(4096)
        return data

    #sends then waits to recieve a response
    def send_recieve_packet(self, packet_type, session_id, payload=b""):
        self.send_packet(self.encode_packet(packet_type, session_id, payload))
        data = self.recieve_packet()
        packet_decoded = self.decode_packet(data)
        return packet_decoded

    #encodes a packet to be sent to the server
    def encode_packet(self, packet_type, session_id, payload=b""):
        packet_type_byte = packet_type.to_bytes(1, byteorder="big")
        packet_pre = struct.pack(">ci", packet_type_byte, self.convert_session_id(session_id))
        
        if packet_type == 9:
            packet_final = b"\xfe\xfd" + packet_pre
        else:
            packet_final = b"\xfe\xfd" + packet_pre + payload + b"\x00\x00"
        return packet_final

    #decodes a packet sent from the server
    def decode_packet(self, packet):
        packet_type = int(packet[0])
        session_id = int(int.from_bytes(packet[1:5], byteorder="big"))
        payload = packet[5:]
        
        return packet_type, session_id, payload

    #converts an int to a valid session_id
    def convert_session_id(self, session_id):
        session_id_converted = session_id
        session_id_converted &= 0x0F0F0F0F
        return session_id_converted

    #get a token from the mc server
    def get_challenge_token(self, session_id=0):
        packet = self.send_recieve_packet(9, session_id)
        return int(packet[2][:-1])

    #basic stat - returns less info
    def basic_stat(self, challenge_token=None, session_id=0):
        if challenge_token == None:
            challenge_token = self.get_challenge_token(session_id)
        challenge_token_bytes = challenge_token.to_bytes(4, byteorder="big")
        packet = self.send_recieve_packet(0, session_id, challenge_token_bytes)
        payload_split = packet[2].split(b"\x00")[:-1]

        stats = {
            "motd": "",
            "gametype": "",
            "map": "",
            "numplayers": "",
            "maxplayers": "",
            "hostport": "",
            "hostip": ""
        }
        index = 0
        for key in stats:
            if key == "hostport":
                port = struct.unpack("<h", payload_split[index][:2])[0]
                ip = payload_split[index][2:].decode("latin-1")
                stats["hostport"] = port
                stats["hostip"] = ip
                break
            if key == "numplayers" or key == "maxplayers":
                stats[key] = int(payload_split[index].decode("latin-1"))
            else:
                #this probably wont work on certain server motds that use special chars
                #but the motd doesn't properly support unicode this is the only way
                #for this to work
                stats[key] = payload_split[index].decode("latin-1")
            index = index + 1
        
        return stats

    #full stat - returns more info
    def full_stat(self, challenge_token=None, session_id=0):
        if challenge_token == None:
            challenge_token = self.get_challenge_token(session_id)
        challenge_token_bytes = challenge_token.to_bytes(4, byteorder="big")
        payload = challenge_token_bytes + b"\x00"*2
        packet = self.send_recieve_packet(0, session_id, payload)

        response_split = packet[2][11:].split(b"\x00\x01player_\x00\x00")
        stats_split = response_split[0].strip(b"\x00").split(b"\x00")
        stats = {}
        for i in range(0, len(stats_split), 2):
            key = stats_split[i].decode()
            value_raw = stats_split[i+1]
            if key in ["numplayers", "maxplayers", "hostport"]:
                value = int(value_raw.decode())
            else:
                value = value_raw.decode("latin-1")
            stats[key] = value

        players_raw = response_split[1].strip(b"\x00").split(b"\x00")
        players = []
        for player in players_raw:
            players.append(player.decode())
        stats["players"] = players
                
        return stats

if __name__ == "__main__":
    
    address = ("127.0.0.1", 25565)

    query = Query(address)
    token = query.get_challenge_token()
    stats = query.full_stat(token)
    print(stats)
