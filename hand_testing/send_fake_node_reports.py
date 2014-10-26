import socket
import time
import random

UDP_IP = "127.0.0.1"
UDP_PORT = 9001
N = 10

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT

def generate_msg():
	ending = random.randint(1, N)
	eui_parts = [0] * 7  + [ending]
	eui = 'EUI-64=' + '-'.join('%02x' % k for k in eui_parts) + ';'
	temp = 'temperature=%.2f^C;' % random.random()
	hum = 'humidity=%.2f%%;' % random.random()
	vol = 'voltage=%.4fV;' % random.random()
	return eui + temp + hum + vol

sock = socket.socket(socket.AF_INET, # Internet
		     socket.SOCK_DGRAM) # UDP

while True:
	msg = generate_msg()
	sock.sendto(msg, (UDP_IP, UDP_PORT))
	print 'Sent: ', (msg, (UDP_IP, UDP_PORT)) 
	time.sleep(1)
