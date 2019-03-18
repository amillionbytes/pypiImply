from sense_hat import SenseHat
from random import getrandbits
from random import randint
from datetime import datetime
from time import sleep
from kafka import KafkaProducer
import json

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
        raise ValueError(
        "pixelProgress : catastrophic miscalculation of the necessary pixel string length!")
    sense.set_pixels(M)

def writeToJson(jsonData, filename):
    try:
        sense.show_letter('W')
        with open(filename, 'w') as outfile:
            json.dump(jsonData, outfile)
        
        producer.send('sensehat',json.dumps(jsonData))
	
    except Exception as error:
        print("Exception Thrown\n", repr(error))

def sampleEnvironment(sensor, samples, decimalPoints, delaySeconds):
    sumTemp = 0
    sumHumd = 0
    sumPres = 0
    reverse=bool(getrandbits(1))
    fillColor = [randint(0,255),randint(0,255),randint(0,255)]
    emptyColor = [randint(0,255),randint(0,255),randint(0,255)]

    for t in range(samples):
        sumTemp += sensor.get_temperature()
        sumHumd += sensor.get_humidity()
        sumPres += sensor.get_pressure()

        pixelProgress((t+1),samples,fillColor,emptyColor,reverse)

        sleep(delaySeconds)

    return {
            "temperature" : str(round(sumTemp / samples, decimalPoints)),
            "humidity" : str(round(sumHumd / samples, decimalPoints)),
            "pressure" : str(round(sumPres / samples, decimalPoints))}

def sampleAverages(sensor):
    # Get a good number of readings from the senseHAT

    sample = sampleEnvironment(sensor,10,4,0.1)

    # Add to the readings

    return({
        'datetime': datetime.now(),
        'temperature': sample["temperature"],
        'humidity': sample["humidity"],
        'pressure': sample["pressure"]})


######################################################################


outputFileFormat = "shed_%Y%m%d%H%M"

# Connect to the senseHat

sense = SenseHat()

# Connect to Kafka

print ('Connecting to Kafka.')
producer = KafkaProducer(bootstrap_servers='brenda.local:9095')
print ('Done.')

# Collect some data until the joystick is activated

try:

    anyJoystickEvents = (len(sense.stick.get_events()) != 0)

    while not anyJoystickEvents:

        outputFile = datetime.now().strftime(outputFileFormat) + ".json"
        oldOutputFile = outputFile
        data = {}
        data["readings"] = []

        while (outputFile == oldOutputFile) and (not anyJoystickEvents):
            averageReadings = sampleAverages(sense)

            # Given the readings, what is the correct name for the output file?

            outputFile = averageReadings["datetime"].strftime(outputFileFormat) + ".json"
            averageReadings["datetime"]=averageReadings["datetime"].isoformat()

            if outputFile != oldOutputFile:
                print ("Writing to new file...", outputFile)
                writeToJson(data, outputFile)
                oldOutputFile = outputFile
                data["readings"] = []

            data["readings"].append(averageReadings)

            anyJoystickEvents = (len(sense.stick.get_events()) != 0)

    writeToJson(data, outputFile)
    producer.flush();

except Exception as error:
    print("Exception Thrown\n", repr(error))

# Tidy up

sense.clear(0,0,0)
produce.close();

print("Finished")
