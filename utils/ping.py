import socket, struct, ctypes, json, time

class Pinger:
    def __init__(self, address=("127.0.0.1", 25565)):
        self.host, self.port = address
        self.address = address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10)
        self.sock.connect(address)

    def encode_varint(self, n):
        digits_list = []
        n = ctypes.c_uint32(n).value
        while True:
            digit = n & 0x7f
            n >>= 7
            if n:
                digits_list.append(digit | 0x80)
            else:
                digits_list.append(digit)
                break
        result = b""
        for digit in digits_list:
            result += digit.to_bytes(1, "little")
        return result

    def decode_varint(self, n):
        result = 0
        i = 0
        while True:
            result |= (n[i] & 0x7f) << (i*7)
            if not (n[i] & 0x80) != 0x80:
                i += 1
            else:       
                return ctypes.c_int32(result).value

    def encode_packet(self, packet_id, data):
        packet = self.encode_varint(packet_id) + data
        packet = self.encode_varint(len(packet)) + packet
        return packet
    
    def decode_packet(self, data):
        index = 0
        for byte in data:
            index += 1
            if not byte >> 7:
                break
        data_length = self.decode_varint(data[:index])
        new_index = index
        
        for byte in data[index:]:
            new_index += 1
            if not byte >> 7:
                break
        packet_id = self.decode_varint(data[index:new_index])

        data_raw = data[new_index:]
        return data_length, packet_id, data_raw

    def encode_string(self, string):
        string_bytes = string.encode("utf-8")
        string_bytes = self.encode_varint(len(string_bytes))+string_bytes
        return string_bytes

    def decode_string(self, data):
        index = 0
        for byte in data:
            index += 1
            if not byte >> 7:
                break
        result = data[index:].decode("utf-8")
        return result

    def send_packet(self, data):
        self.sock.sendall(data)

    def recieve_packet(self):
        data = self.sock.recv(4096)
        packet_length = self.decode_packet(data)[0]
        while True:
            data_length = (len(data)-len(self.encode_varint(packet_length)))
            if data_length >= packet_length:
                return data
            else:
                try:
                    data += self.sock.recv(4096)
                except socket.timeout:
                    return data
            

    def ping(self):
        time_old = round(time.time()*1000)
        handshake_packet_data = self.encode_varint(-1) + self.encode_string(self.host)
        handshake_packet_data += struct.pack(">H", self.port)
        handshake_packet_data += self.encode_varint(1)
        handshake_packet = self.encode_packet(0, handshake_packet_data)
        self.send_packet(handshake_packet)
        self.send_packet(self.encode_packet(0, b""))
        response_raw = self.recieve_packet()
        time_new = round(time.time()*1000)

        stats_raw = self.decode_packet(response_raw)[2]
        stats = json.loads(self.decode_string(stats_raw))
        stats["ping"] = time_new-time_old
        return stats

    def ping_converted(self):
        stats_ping = self.ping()
        players = []
        if "players" in stats_ping and "sample" in stats_ping["players"]:
            for player in stats_ping["players"]["sample"]:
                players.append(player["name"])
        stats = {
            "hostname": stats_ping["description"]["text"],
            "gametype": "SMP",
            "game_id": "MINECRAFT",
            "version": stats_ping["version"]["name"],
            "protocol_version": stats_ping["version"]["protocol"],
            "plugins": "Unknown",
            "map": "Unknown",
            "numplayers": stats_ping["players"]["online"],
            "maxplayers": stats_ping["players"]["max"],
            "hostport": self.address[1],
            "hostip": self.address[0],
            "players": players
        }
        return stats

    def close(self):
        self.sock.close()
