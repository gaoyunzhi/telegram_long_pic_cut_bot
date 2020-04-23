import os
import sys

EXE_FILE = 'pic_bot'

def kill():
	os.system("ps aux | grep ython | grep %s | awk '{print $2}' | xargs kill -9" % EXE_FILE)

def setup(arg = ''):
	kill()
	if arg == 'kill':
		return
	command = 'python3 -u pic_bot.py'
	
	if arg == 'debug':
		os.system(command)
		return

	os.system('nohup %s &' % command)

	if 'notail' not in sys.argv:
		os.system('touch nohup.out')
		os.system('tail -F nohup.out')

if __name__ == '__main__':
	if len(sys.argv) > 1:
		setup(sys.argv[1])
	else:
		setup('')