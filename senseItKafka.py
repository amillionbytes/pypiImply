from kafka import KafkaProducer

kafkaTopic = "xtolpbky-sense"

Producer = KafkaProducer()

#    def delivery_callback(err, msg):
#        if err:
#            sys.stderr.write('%% Message failed delivery: %s\n' % err)
#        else:
#            sys.stderr.write('%% Message delivered to %s [%d]\n' %
#                             (msg.topic(), msg.partition()))
#
#    for line in sys.stdin:
#        try:
#            p.produce(topic, line.rstrip(), callback=delivery_callback)
#        except BufferError as e:
#            sys.stderr.write('%% Local producer queue is full (%d messages awaiting delivery): try again\n' %
#                             len(p))
#        p.poll(0)
#
#    sys.stderr.write('%% Waiting for %d deliveries\n' % len(p))
#    p.flush()