
from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel, Field

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import json
from pydantic import BaseModel

from datetime import datetime
from kafka import KafkaProducer, producer



# Create class (schema) for the incoming  JSON data 
class invoicedata(BaseModel):
    CustomerName: str = Field(..., alias="customerName")    # adding customerName to make DM
    InvoiceNo: str
    StockCode: str
    Description: str
    Quantity: int
    InvoiceDate: str
    UnitPrice: float
    CustomerID: int
    Country: str

    # allow using both field  names and alias
    class Config:
         allow_population_by_field_name = True

# Initialize the App
app = FastAPI()

# Test root endpoint
@app.get("/")
async def root():
    return {"message": "Bonjour Chez vous"}

# Heath Check endpoint
@app.get("/health")
async def health():
    return {"status": "up"}

# Post endpoint to receive data
@app.post("/invoicedata")
async def post_invoice_item(item: invoicedata): 
    print("Message received")
    #print("New item date:", item.InvoiceDate)

    try:
        # Parse and validate the date format
        date = datetime.strptime(item.InvoiceDate, "%d/%m/%Y %H:%M")

        print('Found a timestamp: ', date)

        # Reformat data to a standard format
        item.InvoiceDate = date.strftime("%d-%m-%Y %H:%M:%S")
        print("New item date:", item.InvoiceDate)
        
        # convert the object json to compatible dictionnary
        json_of_item = jsonable_encoder(item)
        
        # Send Json string to Kafka
        json_as_string = json.dumps(json_of_item)
        print(json_as_string)
        
        # Send the Json string to Kafka
        produce_kafka_string(json_as_string)

        #  return the Json response with  201 status code if successfull
        return JSONResponse(content=json_of_item, status_code=201)
    
    # return 400 status code if failed
    except ValueError:
        return JSONResponse(content=jsonable_encoder(item), status_code=400)
        

# Function to send data to Kafka
def produce_kafka_string(json_as_string):
    # Create producer
        producer = KafkaProducer(bootstrap_servers='kafka:9092',acks=1)
        
        # send the data to kafka topic
        producer.send('ingestion-topic', bytes(json_as_string, 'utf-8'))
        producer.flush() 
