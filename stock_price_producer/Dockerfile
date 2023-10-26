FROM python:3.10

# WORKDIR /app

# COPY requirements.txt /app/

# RUN pip install --no-cache-dir -r requirements.txt

# COPY StockPriceSchema.avsc /app/
# COPY stock_price_producer.py /app/

# CMD ["python", "stock_price_producer.py"]

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["python","src/stock_price_producer.py"]