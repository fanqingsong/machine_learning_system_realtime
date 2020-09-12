# coding: utf-8
import time, json
from kafka import KafkaProducer
import requests
from bs4 import BeautifulSoup

web_url = "https://en.wikipedia.org/wiki/COVID-19_pandemic"

class Sender:
    def __init__(self):
        self._producer = KafkaProducer(bootstrap_servers='localhost:9092')

    def _send_iris(self):
        batches = [[5.1, 3.5, 1.4, 0.2]]
        for batch in batches:
            print("sending msg({})".format(json.dumps(batch).encode()))
            self._producer.send('oneIrisData', json.dumps(batch).encode())
            time.sleep(5)

    def execute(self):
        self._send_iris()

if __name__ == "__main__":
    sender = Sender()
    sender.execute()

