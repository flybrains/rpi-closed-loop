import sys
import argparse
import time
import numpy as np
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM

# EXPERIMENT CONFIGS
# 0 = Wait state
# 1 = Closed loop motor, constant odor
# 2 = Closed loop motor, 1D proportional odor

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('LOCAL_HOST')
	parser.add_argument('LOCAL_PORT')
	parser.add_argument('RPI_HOST')
	parser.add_argument('RPI_PORT')
	parser.add_argument('CONFIG')
	parser.add_argument('SRC_DISTANCE')
	parser.add_argument('MAX_AIRFLOW')
	args = parser.parse_args()
	return args.LOCAL_HOST, int(args.LOCAL_PORT), args.RPI_HOST, int(args.RPI_PORT), int(args.CONFIG), int(args.SRC_DISTANCE), int(args.MAX_AIRFLOW)

def establish_pi_connection(RPI_HOST, RPI_PORT):
	PACKET_SIZE = 1024
	sock=socket(AF_INET, SOCK_DGRAM)
	return sock

def convert_angle_for_arduino(inputVal, previousAngle):
	inputVal = inputVal*(256/800)
	spr = 800
	conv1 = spr*(1000/256)
	newAngle1 = (inputVal*conv1)/1000
	highLimit = 450
	lowLimit = 350
	midPoint = 400
	mult = 1000
	offset = mult*spr

	if (newAngle1 < highLimit) and (newAngle1 >lowLimit):
		if(newAngle1 > midPoint):
			newAngle1 = highLimit
		else:
			newAngle1 = lowLimit
	newAngle1 = newAngle1 + offset

	if np.abs(newAngle1-previousAngle) > 400:
		if(newAngle1 > previousAngle):
			mult = mult-1
			offset = mult*spr
			newAngle1 = newAngle1 - spr

		else:
			mult = mult + 1
			offset = mult*spr
			newAngle1 = newAngle1 + spr

	previousAngle = newAngle1

	return newAngle1

def run_fictrac_client(LOCAL_HOST, LOCAL_PORT, RPI_SOCK, RPI_HOST, RPI_PORT, config, src_distance, maxAirFlow):

	for _ in range(10):
		CFGSTRING = '$'+ '{}'.format(config) +'$\n'
		RPI_SOCK.sendto(str.encode('{}'.format(CFGSTRING)), (RPI_HOST, RPI_PORT))

	with socket(AF_INET, SOCK_STREAM) as sock:
		time.sleep(0.02)
		sock.connect((LOCAL_HOST, LOCAL_PORT))
		motorLastTime = time.time()
		odorLastTime = time.time()
		previousAngle = 800000

		mfcVal1, mfcVal2, mfcVal3 = 0, 0, 0
		motorSendVal = 800000

		while True:
			data = sock.recv(1024)
			if not data:
				break
			line = data.decode('UTF-8')
			toks = line.split(',')


			if ((len(toks) < 24) | (toks[0] != "FT")):
				print('Bad read')
				continue

			posy = float(toks[16])
			heading = float(toks[17])
			propHead = heading/6.28

			target = int(propHead*800)
			posy = posy*3

			#print("HEADING[rad]: {}  DISCT HEADING[steps/800]: {} YPOS[mm]: {}".format(heading, target, posy))

			if (time.time() - motorLastTime > (1/30)):

				if config==0:
					correctedTarget = convert_angle_for_arduino(target, previousAngle)
					previousAngle = correctedTarget
					motorSendVal = correctedTarget
					motorLastTime = time.time()

					mfcVal1 = int(100*(maxAirFlow/1000))	#Air Pin
					mfcVal2 = 0		#Odor 1 Pin
					mfcVal3 = 0		#Odor 2 Pin

				if config==1:
					correctedTarget = convert_angle_for_arduino(target, previousAngle)
					previousAngle = correctedTarget
					motorSendVal = correctedTarget
					motorLastTime = time.time()

					if posy >= src_distance:
						mfcVal1 = int(100*(maxAirFlow/1000))
						mfcVal2 = 0
						mfcVal3 = 0
					else:
						mfcVal1 = int((maxAirFlow / 1000)*(posy/src_distance)*100)
						mfcVal1 = max(0, mfcVal1)
						mfcVal2 = int((maxAirFlow / 1000)*(1-(posy/src_distance))*100)
						mfcVal3 = 0

				SENDSTRING = '<'+ '{},{},{},{}'.format(motorSendVal, mfcVal1, mfcVal2, mfcVal3) +'>\n'
				RPI_SOCK.sendto(str.encode('{}'.format(SENDSTRING)), (RPI_HOST, RPI_PORT))

			else:
				pass

if __name__=='__main__':
	LOCAL_HOST, LOCAL_PORT, RPI_HOST, RPI_PORT, config, src_distance, maxAirFlow = parse_args()
	RPI_SOCK  = establish_pi_connection(RPI_HOST, RPI_HOST)
	run_fictrac_client(LOCAL_HOST, LOCAL_PORT, RPI_SOCK, RPI_HOST, RPI_PORT, config, src_distance, maxAirFlow)


















#
