import json
import os
import io
import re
import websocket
import avro.schema
from avro.datafile import DataFileWriter
from avro.io import DatumWriter
from kafka import *

class StockPriceProducer:

    def __init__(self):

        self.producer = KafkaProducer(bootstrap_servers=['localhost:9092'],  api_version=(0,10,2))
        self.KafkaTopic = 'stockPrices'

        self.StockPriceOutput = DataFileWriter(
            open("StockPriceOutput.avro", "wb"), 
            DatumWriter(), 
            avro.schema.parse(open("./Schemas/StockPriceSchema.avsc", "rb").read()))
        
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("wss://ws.finnhub.io?token="+os.getenv("FINNHUB_TOKEN"),
                                    on_message = self.on_message,
                                    on_error = self.on_error,
                                    on_close = self.on_close)
        self.ws.on_open = self.on_open

        self.ws.run_forever()
        self.ws.on_close = self.on_close

        
    def on_message(self, ws, message):
        message_json = json.loads(message)
        
        if message_json['type'] == "trade":
            for singleRecord in message_json['data']:
                self.StockPriceOutput.append(singleRecord)

                with open("./Schemas/StockPriceSchema.avsc", "rb") as schema_file:
                    schema = avro.schema.parse(schema_file.read())
                byteStream = io.BytesIO()
                encoder = avro.io.BinaryEncoder(byteStream)
                avro.io.DatumWriter(schema).write(singleRecord, encoder)

                allowedKeyChars = r'[^a-zA-Z0-9\._\-]'
                
                self.producer.send(topic = self.KafkaTopic, 
                                #    key = re.sub(allowedKeyChars, '', singleRecord['s']).encode('utf-8'), 
                                    key = singleRecord['s'].encode('utf-8'), 
                                   value = byteStream.getvalue())


    def on_error(self, ws, error):
        print(error)
        

    def on_close(self, ws, close_status_code, close_msg):
        print("on_close args:")
        if close_status_code or close_msg:
            print("close status code: " + str(close_status_code))
            print("close message: " + str(close_msg))
        self.StockPriceOutput.close()
        ws.close()

        
    def on_open(self, ws):
        self.ws.send('{"type":"subscribe","symbol":"AMZN"}')
        self.ws.send('{"type":"subscribe","symbol":"GOOG"}')
        self.ws.send('{"type":"subscribe","symbol":"TSLA"}')
        self.ws.send('{"type":"subscribe","symbol":"MSFT"}')
        self.ws.send('{"type":"subscribe","symbol":"NVDA"}')
        self.ws.send('{"type":"subscribe","symbol":"AAPL"}')
        self.ws.send('{"type":"subscribe","symbol":"META"}')
        self.ws.send('{"type":"subscribe","symbol":"BINANCE:BTCUSDT"}')
