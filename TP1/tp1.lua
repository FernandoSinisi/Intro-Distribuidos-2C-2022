tp1_proto = Proto("tp1", "Service State Protocol")
seq_num = ProtoField.uint16("tp1.SeqNum", "SeqNum", base.DEC)
ack_num = ProtoField.uint16("tp1.AckNum", "AckNum", base.DEC)
flags = ProtoField.uint8("tp1.Flags", "Flags", base.DEC)

prot = ProtoField.string("tp1.PROT", "PROT", base.ASCII)
ack = ProtoField.string("tp1.ACK", "ACK", base.ASCII)
syn = ProtoField.string("tp1.SYN", "SYN", base.ASCII)
fin = ProtoField.string("tp1.FIN", "FIN", base.ASCII)
up = ProtoField.string("tp1.UP", "UP", base.ASCII)

tp1_proto.fields = {seq_num, ack_num, flags, prot, ack, syn, fin, up}

function bitand(a, b)
    local result = 0
    local bitval = 1
    while a > 0 and b > 0 do
      if a % 2 == 1 and b % 2 == 1 then -- test the rightmost bits
          result = result + bitval      -- set the current bit
      end
      bitval = bitval * 2 -- shift left
      a = math.floor(a/2) -- shift right
      b = math.floor(b/2)
    end
    return result
end

function bool_to_string(bool, value_true, value_false)
	if bool then
		return value_true
	else
		return value_false
	end
end

function tp1_proto.dissector(buffer, pinfo, tree)
	pinfo.cols.protocol = tp1_proto.name; 
	subtree = tree:add(tp1_proto, buffer())

	flags = buffer(4,1):le_uint()


	bool_to_number={ [true]=1, [false]=0 }

	p = bool_to_string(bitand(flags, tonumber("00010000", 2)) ~= 0, "SAW", "-")
	a = bool_to_string(bitand(flags, tonumber("00001000", 2)) ~= 0, "ACK", "-")
	s = bool_to_string(bitand(flags, tonumber("00000100", 2)) ~= 0, "SYN", "-")
	f = bool_to_string(bitand(flags, tonumber("00000010", 2)) ~= 0, "FIN", "-")
	u = bool_to_string(bitand(flags, tonumber("00000001", 2)) ~= 0, "UP", "DN")

	subtree:add(seq_num, buffer(0,2))
	subtree:add(ack_num, buffer(2,2))
	subtree:add(flags, buffer(4,1))

	subtree:add(prot, p)
	subtree:add(ack, a)
	subtree:add(syn, s)
	subtree:add(fin, f)
	subtree:add(up, u)
end


local udp_port = DissectorTable.get("udp.port")
udp_port:add(8080, tp1_proto)