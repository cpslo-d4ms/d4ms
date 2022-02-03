import socket as sock
import logging as logger
import threading as thread
import cv2 as opencv
import math
import struct
import signal
import time

MAX_DATA_SIZE = 2**16 # maximum payload size for UDP packet is 2^16 = 65536 bytes

UDP_PORT = 49152 # use the first user-allocated port number for UDP communication
UDP_IP = "172.16.0.1" # Ethernet IP address for the Raspberry Pi
BUFFER_SIZE = 65536

NANO_MSG_PORT = 49152
NANO_VID_PORT = 49153
NANO_IP = "172.16.0.2"

# Addresses of the Jetson Nano and Raspberry Pi
# in the form of (IP address, port number) pairs
NANO_MSG_ADDR = ("172.16.0.2", 49152)
NANO_VID_ADDR = ("172.16.0.2", 49153)
RPI_MSG_ADDR = ("172.16.0.1", 49152)

# Global boolean to tell the code when to stop streaming video and clean up
stop_stream = False

def signal_handler(signum, frame):
    global stop_stream 

    stop_stream = True # indicate to the program to exit the streaming loop
    print("\nVideo stopped at user request...")

def generate_udp_frames(data):
    payloadSize = len(data)
    num_packets = math.ceil(payloadSize / (MAX_DATA_SIZE - 64))
    packets = []
    start = 0

    # Generate packets from the string of video bytes
    while num_packets > 0:
        end = min(payloadSize, start + (MAX_DATA_SIZE-64))
        # Add a sequence number to each packet that indicates to the receiver
        # if more packets are incoming for the same video frame
        packet = struct.pack("B", num_packets) + data[start:end]
        packets.append(packet)
        start = end
        num_packets-=1

    return packets


def stream_video():
    vidSock = sock.socket(family=sock.AF_INET,
                          type=sock.SOCK_DGRAM,
                          proto=0)

    vidSock.bind(RPI_MSG_ADDR)
    hello_msg = bytearray("Hello", encoding="utf-8")
    vidSock.sendto(hello_msg, NANO_VID_ADDR)
    data, addr = vidSock.recvfrom(MAX_DATA_SIZE)
    #print("Received message {0} from ({1}, {2})\n".format(data, addr[0], addr[1]))
    # Open video file with data to send
    #vid = opencv.VideoCapture("test.mp4") # video file for testing
    vid = opencv.VideoCapture(0) # capture frames from the Raspberry Pi camera
    while not stop_stream:
       status, frame = vid.read() # read a frame from the video file
       if not status:
           print("Video finished, exiting...")
           break
       compressed = opencv.imencode('.jpg', frame)[1]
       udpFrames = generate_udp_frames(compressed.tostring())
       for i in range(0, len(udpFrames)): # send each frame serially to the Nano
            vidSock.sendto(udpFrames[i], NANO_VID_ADDR)

    # Give receiver time to process its last frame(s) and send an all-done message   
    time.sleep(1)
    vidSock.sendto(struct.pack("!I", 0xdeadbeef), NANO_VID_ADDR) 

    # Release all resources allocated to openCV and the socket
    vid.release()
    opencv.destroyAllWindows()
    vidSock.close()

if __name__ == "__main__":

    # Register the SIGINT handler
    signal.signal(signal.SIGINT, signal_handler)

    
    # Create separate thread for sending video to the Jetson Nano
    sender = thread.Thread(target=stream_video)

    # Start the video streaming thread and wait in this thread until it completes
    sender.start()
    sender.join()
