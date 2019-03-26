from sense_hat import SenseHat
from random import getrandbits
from random import randint
from datetime import datetime
from kafka import KafkaProducer
import subprocess
import json
import socket
import configparser


def pixelProgress(complete, total, fill, empty, reverse):
    if (complete > total):
        raise ValueError("pixelProgress : completed exceeds the total")

    pixelsPerPoint = (64 / total)
    progress = int(round(complete * pixelsPerPoint))
    remaining = 64 - progress

    if reverse:
        M = (remaining * [empty]) + (progress * [fill])
    else:
        M = (progress * [fill]) + (remaining * [empty])

    if (len(M) > 64):
        raise ValueError("pixelProgress : catastrophic miscalculation of the necessary pixel string length!")
    sense.set_pixels(M)


def sampleEnvironment(sensor, samples, decimalPoints):
    # Variable setup
    sumTemp = 0
    sumHumd = 0
    sumPres = 0
    sumCpuTemp = 0

    # Random stuff for the SenseHAT RGBs
    reverse = (bool(getrandbits(1)))
    fillColor = [randint(0, 255), randint(0, 255), randint(0, 255)]
    emptyColor = [randint(0, 255), randint(0, 255), randint(0, 255)]

    # Now take a number of samples of the different sensors

    for t in range(samples):
        sensedTemp = sensor.get_temperature()

        cpu_temp = subprocess.check_output("vcgencmd measure_temp", shell=True)
        array = cpu_temp.split("=")
        array2 = array[1].split("'")

        cpu_tempc = float(array2[0])

        sumCpuTemp += cpu_tempc

        cpu_tempc = float("{0:.2f}".format(cpu_tempc))
        temp_calibrated_c = sensedTemp - ((cpu_tempc - sensedTemp) / 54.66)

        sumTemp += temp_calibrated_c
        sumHumd += sensor.get_humidity()
        sumPres += sensor.get_pressure()

        pixelProgress((t + 1), samples, fillColor, emptyColor, reverse)

    # Return the average

    return {
        "temperature": str(round(sumTemp / samples, decimalPoints)),
        "humidity": str(round(sumHumd / samples, decimalPoints)),
        "pressure": str(round(sumPres / samples, decimalPoints)),
        "hostTemperature": str(round(sumCpuTemp / samples, decimalPoints))}


def sampleAverages(sensor, hostname):
    # Get a good number of readings from the senseHAT

    sample = sampleEnvironment(sensor, 50, 4)

    # Add to the readings for this host

    return ({
        'hostname': hostname,
        'datetime': datetime.now().isoformat(),
        'temperature': sample["temperature"],
        'humidity': sample["humidity"],
        'pressure': sample["pressure"],
        'hostTemperature': sample["hostTemperature"]})


######################################################################


# Get configuration
config = configparser.ConfigParser()
config.read('senseIt.ini')
configKafka = config['Kafka']['bootstrapServer'] + ':' + config['Kafka']['bootstrapServerPort']
print(configKafka)
# Connect to the senseHat, get the hostname, and connect to Kafka

sense = SenseHat()
hostname = socket.gethostname()
print('Connecting to Kafka.')
producer = KafkaProducer(bootstrap_servers=configKafka)
print('Done.')

# Now collect some average data until the joystick is activated

try:

    anyJoystickEvents = (len(sense.stick.get_events()) != 0)

    while not anyJoystickEvents:
        averageReadings = sampleAverages(sense, hostname)
        producer.send('sensehat', json.dumps(averageReadings))
        anyJoystickEvents = (len(sense.stick.get_events()) != 0)

    producer.flush()

except Exception as error:
    print("Exception Thrown\n", repr(error))

    # All done - tidy up

sense.clear(0, 0, 0)
producer.close();

print("Finished")
