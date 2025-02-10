import psycopg2
import pandas as pd




def main():
        # Your script's logic here
        # Connect to PostgreSQL
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="admin",
        host="localhost",  # Change if your database is hosted elsewhere
        port="5433"        # Default PostgreSQL port
    )

    # Create a cursor object
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        product_name TEXT,
        price_value REAL,
        currency TEXT,
        location TEXT,
        product_url TEXT UNIQUE,  -- Add UNIQUE constraint to product_url
        image_url TEXT
    )
    ''')

    # Commit the table creation
    conn.commit()

    # Read the CSV file
    csv_file = "product_details.csv"
    df = pd.read_csv(csv_file)

    # Loop through each row in the DataFrame
    for index, row in df.iterrows():
        cursor.execute('''
        INSERT INTO products (product_name, price_value, currency, location, product_url, image_url)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (product_url) DO UPDATE
        SET product_name = EXCLUDED.product_name,
            price_value = EXCLUDED.price_value,
            currency = EXCLUDED.currency,
            location = EXCLUDED.location,
            image_url = EXCLUDED.image_url;
        ''', (
            row['product_name'],
            row['price_value'],
            row['currency'],
            row['location'],
            row['product_url'],
            row['image_url']
        ))

# Commit and close the connection
    conn.commit()
    conn.close()

    print("Data inserted/updated successfully!")

if __name__ == "__main__":
    main()  # Call the main function