from kafka import KafkaConsumer
from avro.io import DatumReader, BinaryDecoder
import avro.schema
import io

# Create a KafkaConsumer instance
consumer = KafkaConsumer('stockPrices',  # Replace with your topic name
                         bootstrap_servers='localhost:9092',  # Kafka broker(s) address
                         group_id='my_consumer_group',  # Consumer group ID
                         auto_offset_reset='earliest',  # Start from the beginning of the topic
                         enable_auto_commit=True,  # Automatically commit offsets
                         auto_commit_interval_ms=1000)  # Commit offsets every 1 second (adjust as needed)

with open("./Schemas/StockPriceSchema.avsc", "rb") as schema_file:
    schema = avro.schema.parse(schema_file.read())
datumReader = DatumReader(schema)

try:
    for message in consumer:
        # Decode the Avro-encoded message
        message_value = message.value
        message_bytes = io.BytesIO(message_value)
        decoder = BinaryDecoder(message_bytes)
        avroData = datumReader.read(decoder)

        # Process the Avro data (avro_data) as needed
        print("Received Avro data:", avroData)

except KeyboardInterrupt:
    pass
finally:
    consumer.close()