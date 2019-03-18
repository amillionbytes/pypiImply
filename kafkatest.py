from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='brenda.local:9095')

for _ in range(100):
	producer.send('sensehat', b'some_message_bytes')
	print ('sent ', _)
	
	
