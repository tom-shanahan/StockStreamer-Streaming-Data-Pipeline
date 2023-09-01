import websocket
import json
import os
import avro.schema
from avro.datafile import DataFileWriter
from avro.io import DatumWriter

class StockPriceProducer:

    def __init__(self):

        websocket.enableTrace(True)
        self.StockPriceOutput = DataFileWriter(
            open("StockPriceOutput.avro", "wb"), 
            DatumWriter(), 
            avro.schema.parse(open("./Schemas/StockPriceSchema.avsc", "rb").read()))
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
            self.StockPriceOutput.append(message_json)


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
