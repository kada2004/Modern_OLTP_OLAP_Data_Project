import psycopg2
from psycopg2 import Error
from decouple import config

# Loading database parameters from .env file
db_params = {
    "dbname": config('POSTGRES_DB'),
    "user": config('POSTGRES_USER'),
    "password": config('POSTGRES_PASSWORD'),
    "host": config('POSTGRES_HOST', default='localhost'),  
    "port": config('POSTGRES_PORT', default='5432')       
}

# SQL script to create database tables
create_tables_sql = """
-- Table: Customer
CREATE TABLE Customer (
    CustomerID INT PRIMARY KEY
    CustomerName VARCHAR(255)
);

-- Table: Country
CREATE TABLE Country (
    CountryID SERIAL PRIMARY KEY,
    Country_Name VARCHAR(255),
    CustomerID INT,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID)
);

-- Table: Invoice
CREATE TABLE Invoice (
    InvoiceNo INT PRIMARY KEY,
    CustomerID INT,
    InvoiceDate TIMESTAMP,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID)
);

-- Table: Stock
CREATE TABLE Stock (
    StockID SERIAL PRIMARY KEY,
    StockCode INT,
    Description VARCHAR(255),
    Quantity INT,
    UnitPrice DOUBLE PRECISION,
    invoice_url TEXT
);

-- Table: InvoiceStock
CREATE TABLE InvoiceStock (
    InvoiceStockCodeID SERIAL PRIMARY KEY,
    InvoiceNo INT,
    StockID INT,
    FOREIGN KEY (InvoiceNo) REFERENCES Invoice(InvoiceNo),
    FOREIGN KEY (StockID) REFERENCES Stock(StockID)
);

-- Indexes
CREATE INDEX idx_country_customer ON Country(CustomerID);
CREATE INDEX idx_invoice_customer ON Invoice(CustomerID);
CREATE INDEX idx_invoicestock_invoice ON InvoiceStock(InvoiceNo);
CREATE INDEX idx_invoicestock_stock ON InvoiceStock(StockID);
"""

try:
    # Establish connection to PostgreSQL
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()

    # Execute the SQL script
    cursor.execute(create_tables_sql)
    connection.commit()
    print("Tables created successfully in PostgreSQL.")

except (Exception, Error) as error:
    print(f"Error while connecting to PostgreSQL or creating tables: {error}")

finally:
    # Close the connection
    if cursor:
        cursor.close()
    if connection:
        connection.close()
        print("Database connection closed.")