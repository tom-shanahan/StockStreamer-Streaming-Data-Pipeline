import json
import os
import io
import pandas as pd
import websocket
import avro.schema
from avro.datafile import DataFileWriter
from avro.io import DatumWriter
from kafka import *

class StockPriceProducer:

    def __init__(self):

        self.producer = KafkaProducer(bootstrap_servers=['localhost:9092'],  api_version=(0,10,2))
        self.KafkaTopic = 'stockPrices'

        with open("./Schemas/StockPriceSchema.avsc", "rb") as schema_file:
            self.schema = avro.schema.parse(schema_file.read())

        self.StockPriceOutput = DataFileWriter(
            open("StockPriceOutput.avro", "wb"), 
            DatumWriter(), 
            self.schema)
        
        self.streamingTickers = pd.read_csv("BatchProcessing/SteamingTickers.csv").stack().tolist()
        
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


                byteStream = io.BytesIO()
                encoder = avro.io.BinaryEncoder(byteStream)
                avro.io.DatumWriter(self.schema).write(singleRecord, encoder)
                
                self.producer.send(topic = self.KafkaTopic, 
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
        for sym in self.streamingTickers:
            self.ws.send('{"type":"subscribe","symbol":"'+sym+'"}')


if __name__ == "__main__":
    Stock_Price_Producer = StockPriceProducer()
