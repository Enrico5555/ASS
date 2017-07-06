from struct import pack, unpack
class Router:
	def __init__(self, ip, mask):
		self.ip = ip
		self.mask = mask
		self.route = []

	def exend_route(self, route):
		self.route.extend(route)

	def add_to_route(self, as_id):
		self.route.insert(0,as_id)

	def __str__(self):
		return "{ 'ip': "+ip+", 'mask': "+mask+ ", 'route': "+str(route)+ " }"

	def __repr__(self):
		return "{ 'ip': "+ip+", 'mask': "+mask+ ", 'route': "+str(route)+ " }"

def parse_reachability_packet(buffer):
	b = []
	b = unpack("=Bhi",buffer[:7]);
	as_id = b[1]
	destination_amount = b[2]
	destinations = []
	byte_idx=7;
	for i in range(0,destination_amount):
		b = unpack("=BBBBBBBBh",buffer[byte_idx:byte_idx+10])
		ip = str(b[0])+"."+str(b[1])+"."+str(b[2])+"."+str(b[3])
		mask  = str(b[4])+"."+str(b[5])+"."+str(b[6])+"."+str(b[7])
		as_amount = b[8]
		router = Router(ip,mask)
		route = []
		byte_idx= byte_idx+10
		for j in range(0,as_amount):
			route.append(unpack("=h",buffer[byte_idx:byte_idx+2]))
			byte_idx=byte_idx+2
		router.route = route;
		destinations.append(router)
	return {'as_id':as_id,'destinations':destinations}



if __name__ == "__main__":
	parse_reachability_packet(b'\x05\x01\x00\x00\x00\x19\nJ\x01\x03\x03\x03\x03\x01\x00\x00')
