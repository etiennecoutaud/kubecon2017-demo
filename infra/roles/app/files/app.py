#!/usr/bin/env python
from prometheus_client import start_http_server, Counter, Summary
import threading, logging, time, random, string
import multiprocessing

from kafka import KafkaConsumer, KafkaProducer

class Producer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        producer = KafkaProducer(bootstrap_servers='192.168.201.12:9092')
        topics = ['topics-a', 'topics-b']
        rand_str = lambda n: ''.join([random.choice(string.lowercase) for i in xrange(n)])
        i = 0
        c = Counter('injected_message', 'Counter wich count the number of injected message by topic', ['topic'])
        while not self.stop_event.is_set():
            t = topics[random.randint(0,1)]
            s = rand_str(random.randint(100,10000))
            prog = ((i * 100)/10000)
            print("[" + str(prog) + "%] Message (" + s + ") send in topic :" + t)
            producer.send(t, s)
            time.sleep(1)
            i += 1
            c.labels(topic=t).inc()
            if self.stop_event.is_set():
                break

        producer.close()

class ConsumerA(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.stop_event = multiprocessing.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        consumer = KafkaConsumer(bootstrap_servers='192.168.201.12:9092',
                                 auto_offset_reset='earliest',
                                 consumer_timeout_ms=1000)
        consumer.subscribe(['topics-a'])
        c = Counter('read_message', 'Counter wich count the number of injected message by topic', ['topic'])
        while not self.stop_event.is_set():
            for message in consumer:
                print(message)
                c.labels(topic='topic-a').inc()
                if self.stop_event.is_set():
                    break

        consumer.close()


class ConsumerB(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.stop_event = multiprocessing.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        consumer = KafkaConsumer(bootstrap_servers='192.168.201.12:9092',
                                 auto_offset_reset='earliest',
                                 consumer_timeout_ms=1000)
        consumer.subscribe(['topics-b'])
        c = Counter('read_message', 'Counter wich count the number of injected message by topic', ['topic'])
        while not self.stop_event.is_set():
            for message in consumer:
                print(message)
                c.labels(topic='topic-b').inc()
                if self.stop_event.is_set():
                    break

        consumer.close()

def main():
    start_http_server(8000)

    tasks = [
        Producer(),
        ConsumerA(),
        ConsumerB()
    ]
    for task in tasks:
        task.start()

    time.sleep(45)

    for task in tasks:
        task.stop()

    for task in tasks:
        task.join()

    sys.exit(1)

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
        level=logging.INFO
        )
    main()
