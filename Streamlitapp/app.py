import streamlit as st
import psycopg2
import pandas as pd
from decouple import config
from datetime import datetime
import pandas

# Verify pandas version
if not (1.4 <= float(pandas.__version__.split('.')[0]) + float(pandas.__version__.split('.')[1])/10 < 3):
    st.error(f"Streamlit requires pandas>=1.4.0,<3, but found pandas=={pandas.__version__}")
    st.stop()

# Database connection function
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=config('POSTGRES_HOST', default='localhost'),
            port=config('POSTGRES_PORT', default='5432'),
            database=config('POSTGRES_DB', default='spark_db'),
            user=config('POSTGRES_USER', default='spark_user'),
            password=config('POSTGRES_PASSWORD')
        )
        return conn
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        return None

# Fetch all customers
@st.cache_data
def get_customers():
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT CustomerID FROM Customer ORDER BY CustomerID")
            customers = [row[0]  for row in cur.fetchall()]
        conn.close()
        return customers
    except Exception as e:
        st.error(f"Error fetching customers: {e}")
        conn.close()
        return []

# Calculate total spend for a customer
def get_total_spend(customer_id):
    conn = get_db_connection()
    if conn is None:
        return 0.0
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT SUM(s.Quantity * s.UnitPrice) as total_spend
                FROM Invoice i
                JOIN InvoiceStock ist ON i.InvoiceNo = ist.InvoiceNo
                JOIN Stock s ON ist.StockID = s.StockID
                WHERE i.CustomerID = %s
                AND i.InvoiceNo NOT LIKE 'C%%'
            """, (customer_id,))
            result = cur.fetchone()
            total_spend = result[0] if result[0] is not None else 0.0
        conn.close()
        return total_spend
    except Exception as e:
        st.error(f"Error calculating total spend: {e}")
        conn.close()
        return 0.0

# Fetch order history for a customer
def get_order_history(customer_id):
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    try:
        query = """
            SELECT i.InvoiceNo, i.InvoiceDate, SUM(s.Quantity * s.UnitPrice) as Amount,
                   SUM(s.Quantity) as Quantity,
                   STRING_AGG(s.Description, ', ') as ItemsPurchased
            FROM Invoice i
            JOIN InvoiceStock ist ON i.InvoiceNo = ist.InvoiceNo
            JOIN Stock s ON ist.StockID = s.StockID
            WHERE i.CustomerID = %s
            GROUP BY i.InvoiceNo, i.InvoiceDate
            ORDER BY i.InvoiceDate DESC
        """
        df = pd.read_sql_query(query, conn, params=(customer_id,))
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error fetching order history: {e}")
        conn.close()
        return pd.DataFrame()

# Fetch invoice details
def get_invoice_details(invoice_no):
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    try:
        query = """
            SELECT i.InvoiceNo, i.InvoiceDate, i.CustomerID, c.Country_Name,
                   s.StockCode, s.Description, s.Quantity, s.UnitPrice,
                   (s.Quantity * s.UnitPrice) as Total
            FROM Invoice i
            JOIN InvoiceStock ist ON i.InvoiceNo = ist.InvoiceNo
            JOIN Stock s ON ist.StockID = s.StockID
            LEFT JOIN Country c ON i.CustomerID = c.CustomerID
            WHERE i.InvoiceNo = %s
        """
        df = pd.read_sql_query(query, conn, params=(invoice_no,))
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error fetching invoice details: {e}")
        conn.close()
        return pd.DataFrame()

# Fetch returned items (invoices starting with 'C')
def get_returned_items(customer_id):
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    try:
        query = """
            SELECT i.InvoiceNo, i.InvoiceDate, s.StockCode, s.Description, 
                   s.Quantity, s.UnitPrice, (s.Quantity * s.UnitPrice) as Total
            FROM Invoice i
            JOIN InvoiceStock ist ON i.InvoiceNo = ist.InvoiceNo
            JOIN Stock s ON ist.StockID = s.StockID
            WHERE i.CustomerID = %s AND i.InvoiceNo LIKE 'C%%'
            ORDER BY i.InvoiceDate DESC
        """
        df = pd.read_sql_query(query, conn, params=(customer_id,))
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error fetching returned items: {e}")
        conn.close()
        return pd.DataFrame()

# Streamlit app
st.title("Customer Dashboard")

# Sidebar for customer selection
st.sidebar.header("Select Customer")
customer_ids = get_customers()
if not customer_ids:
    st.sidebar.error("No customers found. Please check database connection.")
    st.stop()

customer_id = st.sidebar.selectbox("Customer ID", customer_ids)

# Total Spend
st.header(f"Total Spend for Customer {customer_id}")
total_spend = get_total_spend(customer_id)
st.metric("Total Spend (Excluding Returns)", f"£{total_spend:,.2f}")

# Order History
st.header("Order History")
order_history = get_order_history(customer_id)
if not order_history.empty:
    st.dataframe(
        order_history.rename(columns={
            "invoiceno": "Invoice No",
            "invoicedate": "Date",
            "amount": "Amount (£)",
            "quantity": "Quantity",
            "itemspurchased": "Items Purchased"
        }),
        use_container_width=True
    )
else:
    st.write("No orders found for this customer.")

# Query Invoice Details
st.header("Query Invoice Details")
invoice_nos = order_history["invoiceno"].tolist() if not order_history.empty else []
selected_invoice = st.selectbox("Select Invoice No", ["Select an invoice"] + invoice_nos)
if selected_invoice != "Select an invoice":
    invoice_details = get_invoice_details(selected_invoice)
    if not invoice_details.empty:
        st.dataframe(
            invoice_details.rename(columns={
                "invoiceno": "Invoice No",
                "invoicedate": "Date",
                "customerid": "Customer ID",
                "country_name": "Country",
                "stockcode": "Stock Code",
                "description": "Description",
                "quantity": "Quantity",
                "unitprice": "Unit Price (£)",
                "total": "Total (£)"
            }),
            use_container_width=True
        )
    else:
        st.write("No details found for this invoice.")

# Returned Items
st.header("Returned Items")
returned_items = get_returned_items(customer_id)
if not returned_items.empty:
    st.dataframe(
        returned_items.rename(columns={
            "invoiceno": "Invoice No",
            "invoicedate": "Date",
            "stockcode": "Stock Code",
            "description": "Description",
            "quantity": "Quantity",
            "unitprice": "Unit Price (£)",
            "total": "Total (£)"
        }),
        use_container_width=True
    )
else:
    st.write("No returned items found for this customer.")

# Generate Invoice Button (Placeholder)
st.header("Generate Invoice")
if st.button("Generate Invoice"):
    st.info("Invoice generation is not yet implemented. This will store invoices in blob storage and update Stock.invoice_url.")