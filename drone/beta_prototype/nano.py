import socket as sock
import logging
import threading as thread
import cv2 as opencv
import numpy as np
import struct

# IP address and port number for the Jetson Nano
NANO_ADDR = ("172.16.0.2", 49152)

# IP address and port number for the Raspberry Pi
RPI_ADDR = ("172.16.0.1", 49152)

# Maximum allowed data tranfser size over Ethernet
MAX_DATA_SIZE = 2**16


def dump_buffer(frame):
    while True:
        seg, addr = frame.recvfrom(MAX_DATA_SIZE)
        if struct.unpack("B", seg[0:1])[0] == 1:
            print("finished emptying buffer")
            break

def receive_video():
    vidSock = sock.socket(family=sock.AF_INET, type=sock.SOCK_DGRAM, proto=0)

    # Bind the UDP video socket to the desired port and IP address
    try:
        vidSock.bind(NANO_ADDR)
        logger.info("Bound receiver to video addr (IP: %s, Port: %d)\n", NANO_ADDR[0], NANO_ADDR[1])
        data, addr = vidSock.recvfrom(MAX_DATA_SIZE)
        vidSock.sendto(b'Hello Nano', RPI_ADDR)
        data = b'' # data buffer to read into
        dump_buffer(vidSock)

        # Define the video codec for MP4 files (codec = encoder and decoder for video compression)
        codec = opencv.VideoWriter_fourcc(*'mp4v')

        # Define handler for saving video to an output file
        #                           File name         codec   fps  frame size
        out = opencv.VideoWriter("camera_output.mp4", codec, 20.0, (640, 480))

        while True:
            packet, addr = vidSock.recvfrom(MAX_DATA_SIZE)

            # Check if the incoming packet is a signal from the RPi to stop listening for video feed
            if struct.unpack("!I", packet[0:4])[0] == 0xdeadbeef:
                print("Received all done from sender...")
                break

            # Check if we've reached the last sequence number for the packets making up the current frame
            if struct.unpack("B", packet[0:1])[0] > 1:
                data += packet[1:]
            else:
                data += packet[1:]
                frame = opencv.imdecode(np.fromstring(data, dtype=np.uint8), 1)

                # Write current frame to the output file
                out.write(frame)

                # Display the current frame to the screen
                opencv.imshow("Raspberry Pi Camera", frame)
                
                if opencv.waitKey(1) & 0XFF == ord('q'):
                    break
                data = b'' # empty data buffer for next image frame
        
        # Release all resources allocated by openCV
        out.release()
        opencv.destroyAllWindows()
        vidSock.close()

    except sock.error as msg:
        logger.error("bind() call raised exception: %s\n", msg.strerror)


        
if __name__ == "__main__":

    # Configure logging info for this application (show all debug info by default)
    logging.basicConfig(format='%(asctime)s | %(levelname)s: %(message)s', level=logging.NOTSET)
    nano_logger = logging.getLogger("nano")

    # Begin running the application
    receive_video()
