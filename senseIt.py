import json
import socket
import subprocess
from datetime import datetime
from backports import configparser
from kafka import KafkaProducer
from sense_hat import SenseHat


def take_reading():
    decimal_points = 4

    cpu_temp = subprocess.check_output("vcgencmd measure_temp", shell=True)
    array = cpu_temp.split("=")
    array2 = array[1].split("'")
    cpu_temp_c = float(array2[0])
    cpu_temp_c = float("{0:.2f}".format(cpu_temp_c))
    return_host_temp = cpu_temp_c

    sensed_temp = sense.get_temperature()
    if  config_calibrate = 'true':
        return_temp = sensed_temp - ((cpu_temp_c - sensed_temp) / 54.66)
    else:
        return_temp = sensed_temp

    return ({
        'hostname': config_hostname,
        'datetime': datetime.utcnow().isoformat(),
        'temperature': str(round(return_temp, decimal_points)),
        'humidity': str(round(sense.get_humidity(), decimal_points)),
        'pressure': str(round(sense.get_pressure(), decimal_points)),
        'hostTemperature': str(round(return_host_temp, decimal_points))})

######################################################################
# Get configuration
config = configparser.ConfigParser()
config.read('senseIt.ini')
config_kafka = config['Kafka']['bootstrapServer'] + ':' + config['Kafka']['bootstrapServerPort']
config_hostname = config['PyPiImply']['hostname']
config_topic = config['Kafka']['topic']
config_calibrate = config['PyPiImply']['calibrate_temp']
print(config_kafka)

# Connect to the senseHat, get the hostname, and connect to Kafka

sense = SenseHat()
sense.clear(0, 0, 0)
hostname = socket.gethostname()
print('Connecting to Kafka.')
producer = KafkaProducer(bootstrap_servers=config_kafka)
print('Collecting sensor readings.  Move the joystick to stop.')

# Now collect some average data until the joystick is activated

try:

    anyJoystickEvents = (len(sense.stick.get_events()) != 0)

    while not anyJoystickEvents:
        producer.send(config_topic, json.dumps(take_reading()))
        anyJoystickEvents = (len(sense.stick.get_events()) != 0)

    producer.flush()

except Exception as error:
    print("Exception Thrown\n", repr(error))

    # All done - tidy up

sense.clear(0, 0, 0)
producer.close()

print("Finished")