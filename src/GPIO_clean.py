import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

GPIO.setup(17,GPIO.OUT)
GPIO.setup(23,GPIO.OUT)
GPIO.setup(4,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18,GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.cleanup()
