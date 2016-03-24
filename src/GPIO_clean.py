import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

GPIO.setup(11,GPIO.OUT)
GPIO.setup(12,GPIO.OUT)
GPIO.setup(7,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(16,GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.cleanup()
