import sys
import argparse
import time
import numpy as np
import config
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM


def establish_pi_connection(RPI_HOST, RPI_PORT):
	PACKET_SIZE = 1024
	sock=socket(AF_INET, SOCK_DGRAM)
	return sock

def convert_angle_for_arduino(inputVal, previousAngle, mult):
	inputVal = inputVal*(256/800)
	spr = 800
	conv1 = spr*(1000/256)
	newAngle1 = (inputVal*conv1)/1000
	highLimit = 450
	lowLimit = 350
	midPoint = 400
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

	return newAngle1, mult

def run_fictrac_client(LOCAL_HOST, LOCAL_PORT, RPI_HOST, RPI_PORT):

	RPI_SOCK  = establish_pi_connection(RPI_HOST, RPI_HOST)

	with socket(AF_INET, SOCK_STREAM) as sock:
		time.sleep(0.02)
		sock.connect((LOCAL_HOST, LOCAL_PORT))

		mfc1_sp, mfc2_sp, mfc3_sp = 0.0, 0.0, 0.0
		led1_sp, led2_sp = 0.0, 0.0
		motorSendVal = 800000
		expStartTime = time.time()
		LEDLastTime = expStartTime
		odorLastTime = expStartTime
		motorLastTime = expStartTime
		stimLastTime = expStartTime
		slidingWindow = [[0,0,0,0],[0,0,0,0]]
		activating=False
		stim = False
		previousAngle = 800000
		mult = 1000

		try:
			while True:
				data = sock.recv(1024)
				if not data:
					break
				line = data.decode('UTF-8')
				toks = line.split(',')

				if ((len(toks) < 24) | (toks[0] != "FT")):
					print('Bad read')
					continue

				posx = float(toks[15])*3
				posy = -float(toks[16])*3
				net_vel = float(toks[19])*3
				heading = float(toks[17])
				propHead = heading/6.28
				target = int(propHead*800)

				if len(slidingWindow) >= config.SLIDING_WINDOW_LENGTH:
					slidingWindow.pop(0)
				slidingWindow.append([posx, posy, net_vel, heading])

				if (time.time() - motorLastTime) > (1/30):

					correctedTarget, mult = convert_angle_for_arduino(target, previousAngle, mult)
					previousAngle, motorSendVal = correctedTarget, correctedTarget
					motorLastTime = time.time()

					if config.PROPORTIONAL_ODOR==False:
						mfc1_sp = float(config.FLOW_RATE / 1000)	#air
						mfc2_sp = 0.0								#odor1
						mfc3_sp = 0.0								#odor2
					else:
						if config.N_ODOR_SOURCES == 1:
							if posy >= config.SOURCE:
								mfc1_sp = float(config.MAX_TOTAL_AIRFLOW/1000)
								mfc2_sp = 0.0
								mfc3_sp = 0.0
							else:
								mfc1_sp = float((config.MAX_TOTAL_AIRFLOW / 1000)*(posy/config.SOURCE_1_Y_DISTANCE))
								mfc1_sp = max(0, mfc1_sp)
								mfc2_sp = float((config.MAX_TOTAL_AIRFLOW / 1000)*(1-(posy/config.SOURCE_1_Y_DISTANCE)))
								mfc3_sp = 0.0

					if config.LED_ACTIVATION:
						if config.STIMULATION_MODE == 't':
							if (time.time() - expStartTime) >= config.INITIAL_LED_DELAY:
								if ((time.time() - LEDLastTime) >= config.PERIOD_BETWEEN_PULSE_RISING_EDGES):
									if activating==False:
										activating = True
										pulseStarted = time.time()

										if config.LED_COLOR=='red':
											led1_sp = config.LED_INTENSITY
											led2_sp = 0.0
										else:
											led1_sp = 0.0
											led2_sp = config.LED_INTENSITY

									elif activating==True and (time.time()-pulseStarted)<=config.DURATION_OF_PULSE_T:
										pass
									else:
										activating=False
										led1_sp = 0.0
										led2_sp = 0.0
										LEDLastTime = pulseStarted

						if config.STIMULATION_MODE == 'c':
							if config.CONDITION_TO_USE==1:
								d = np.diff([i[1] for i in slidingWindow])
								da = np.mean(d)
								if da >= config.CONDITION_THRESHOLD:
									stim=True
							# ++++++++++++++++++++++++++++++++++++
							# ADD MORE KINEMATIC CONDITIONS HERE
							# ++++++++++++++++++++++++++++++++++++
							if stim and (time.time() - stimLastTime)>=config.LOCKOUT_TIME_AFTER_PULSE:
								if activating==False:
									activating = True
									pulseStarted = time.time()

									if config.LED_COLOR=='red':
										led1_sp = config.LED_INTENSITY
										led2_sp = 0.0
									else:
										led1_sp = 0.0
										led2_sp = config.LED_INTENSITY

								elif activating and (time.time()-pulseStarted)<=config.DURATION_OF_PULSE_C:
									pass
								else:
									activating = False
									stim = False
									stimLastTime = pulseStarted
									led1_sp = 0.0
									led2_sp = 0.0

					else:
						led1_sp = 0.0
						led2_sp = 0.0

					SENDSTRING = '<'+ '{},{},{},{},{},{},{}'.format(1,motorSendVal, mfc1_sp, mfc2_sp, mfc3_sp, led1_sp, led2_sp) +'>\n'
					RPI_SOCK.sendto(str.encode('{}'.format(SENDSTRING)), (RPI_HOST, RPI_PORT))
			else:
				pass

		except KeyboardInterrupt:
			SENDSTRING = '<'+ '{},{},{},{},{},{},{}'.format(0, mfcVal1, mfcVal2, mfcVal3) +'>\n'
			RPI_SOCK.sendto(str.encode('{}'.format(SENDSTRING)), (RPI_HOST, RPI_PORT))


if __name__=='__main__':
	config.check_cfg()
	LOCAL_HOST, LOCAL_PORT = config.LOCAL_HOST, config.LOCAL_PORT
	RPI_HOST, RPI_PORT = config.RPI_HOST, config.RPI_PORT
	run_fictrac_client(LOCAL_HOST, LOCAL_PORT, RPI_HOST, RPI_PORT)


















#
