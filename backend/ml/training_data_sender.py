# coding: utf-8
import json, time, pprint
from kafka import KafkaProducer
from celery import shared_task

class Sender:
    def __init__(self):
        self._producer = KafkaProducer(bootstrap_servers='localhost:9092')

    def send(self, batches):
        for batch in batches:
            print("batch type: {}".format(type(batch)))
            print("batch: ({})".format(batch))
            print("sending msg({})".format(json.dumps(batch).encode()))
            self._producer.send('oneIrisData', json.dumps(batch).encode())
            time.sleep(1)

@shared_task
def send_iris_data(batches):
    print('Enter call function ...')
    print("---- batches -------")
    pprint.pprint(batches)
    
    sender = Sender()
    sender.send(batches)


if __name__ == "__main__":
    batches = [[5.1, 3.5, 1.4, 0.2]]

    sender = Sender()
    sender.send(batches)

