
class Packet:

    def __init__(self, seq_num, ack_num, saw, ack, syn, fin, upload, data):
        if ack_num is None:
            ack_num = 0
        self.seq_num = seq_num
        self.ack_num = ack_num
        self.ack = ack
        self.syn = syn
        self.fin = fin
        self.upload = upload
        self.saw = saw
        self.data = data

    def to_bytes(self):
        bytes = b""
        bytes += self.seq_num.to_bytes(2, "big")
        bytes += self.ack_num.to_bytes(2, "big")
        flags = self.saw
        flags <<= 1
        flags += self.ack
        flags <<= 1
        flags += self.syn
        flags <<= 1
        flags += self.fin
        flags <<= 1
        flags += self.upload
        bytes += flags.to_bytes(1, "big")
        bytes += self.data
        return bytes
    
    @classmethod
    def from_bytes(self, bytes):
        seq_num = int.from_bytes(bytes[0:2], "big")
        ack_num = int.from_bytes(bytes[2:4], "big")
        upload = (bytes[4] % 2)
        fin = (bytes[4] >> 1) % 2
        syn = (bytes[4] >> 2) % 2
        ack = (bytes[4] >> 3) % 2
        saw = (bytes[4] >> 4) % 2
        data = bytes[5:]
        return Packet(seq_num, ack_num, saw, ack, syn, fin, upload, data)
    
    def __repr__(self):
        return f"SeqNum: {self.seq_num}, AckNum: {self.ack_num}, ACK: {self.ack}, SYN: {self.syn}, FIN: {self.fin}, UP: {self.upload}, SAW: {self.saw}"#, Data: {self.data[0]}"
