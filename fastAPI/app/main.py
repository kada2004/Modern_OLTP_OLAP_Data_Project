
from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel, Field

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import json
from pydantic import BaseModel

from datetime import datetime
from kafka import KafkaProducer, producer



# Create class (schema) for the JSON
# Date get's ingested as string and then before writing validated
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

    class Config:
         allow_population_by_field_name = True

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Bonjour Chez vous"}

@app.get("/health")
async def health():
    return {"status": "up"}

@app.post("/invoicedata")
async def post_invoice_item(item: invoicedata): 
    print("Message received")
    #print("New item date:", item.InvoiceDate)

    try:
       
        date = datetime.strptime(item.InvoiceDate, "%d/%m/%Y %H:%M")

        print('Found a timestamp: ', date)

        item.InvoiceDate = date.strftime("%d-%m-%Y %H:%M:%S")
        print("New item date:", item.InvoiceDate)
        
        json_of_item = jsonable_encoder(item)
        

        json_as_string = json.dumps(json_of_item)
        print(json_as_string)
        
        # Produce the string
        produce_kafka_string(json_as_string)

        # Encode the created customer item if successful into a JSON and return it to the client with 201
        return JSONResponse(content=json_of_item, status_code=201)
    
    # Will be thrown by datetime if the date does not fit
    # All other value errors are automatically taken care of because of the InvoiceItem Class
    except ValueError:
        return JSONResponse(content=jsonable_encoder(item), status_code=400)
        

def produce_kafka_string(json_as_string):
    # Create producer
        producer = KafkaProducer(bootstrap_servers='kafka:9092',acks=1)
        
        # Write the string as bytes because Kafka needs it this way
        producer.send('ingestion-topic', bytes(json_as_string, 'utf-8'))
        producer.flush() 
