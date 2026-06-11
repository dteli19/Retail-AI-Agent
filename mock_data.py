import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()
random.seed(42)

def generate_customers(n=200):
    segments = ['Champions', 'Loyal', 'At Risk', 'Lost', 'New']
    regions = ['North', 'South', 'East', 'West']
    genders = ['M', 'F']
    
    customers = []
    for i in range(1, n+1):
        customers.append({
            'customer_id': f'CUST{i:04d}',
            'name': fake.name(),
            'age': random.randint(18, 70),
            'gender': random.choice(genders),
            'region': random.choice(regions),
            'segment': random.choice(segments),
            'signup_date': fake.date_between(start_date='-3y', end_date='today')
        })
    return pd.DataFrame(customers)

def generate_transactions(customers_df, n=1000):
    categories = ['Electronics', 'Clothing', 'Groceries', 'Home & Kitchen', 'Beauty']
    stores = ['Store_NYC', 'Store_LA', 'Store_Chicago', 'Store_Houston', 'Store_Phoenix']
    
    transactions = []
    for i in range(1, n+1):
        customer = customers_df.sample(1).iloc[0]
        date = fake.date_between(start_date='-1y', end_date='today')
        category = random.choice(categories)
        transactions.append({
            'transaction_id': f'TXN{i:05d}',
            'customer_id': customer['customer_id'],
            'date': date,
            'category': category,
            'product': fake.word().capitalize() + ' ' + category.split()[0],
            'store': random.choice(stores),
            'quantity': random.randint(1, 5),
            'unit_price': round(random.uniform(10, 500), 2),
            'total_amount': round(random.uniform(10, 2000), 2),
            'discount_applied': random.choice([True, False])
        })
    return pd.DataFrame(transactions)

def generate_promotions(n=50):
    channels = ['Email', 'SMS', 'Social Media', 'In-Store', 'App']
    promo_types = ['Discount', 'BOGO', 'Cashback', 'Free Shipping']
    
    promotions = []
    for i in range(1, n+1):
        start = fake.date_between(start_date='-1y', end_date='-1m')
        end = start + timedelta(days=random.randint(7, 30))
        promotions.append({
            'promo_id': f'PROMO{i:03d}',
            'promo_name': fake.catch_phrase(),
            'promo_type': random.choice(promo_types),
            'channel': random.choice(channels),
            'discount_pct': random.randint(5, 50),
            'start_date': start,
            'end_date': end,
            'redemptions': random.randint(10, 500),
            'revenue_generated': round(random.uniform(1000, 50000), 2),
            'cost': round(random.uniform(500, 10000), 2)
        })
    return pd.DataFrame(promotions)

def load_data():
    customers = generate_customers()
    transactions = generate_transactions(customers)
    promotions = generate_promotions()
    return customers, transactions, promotions

if __name__ == '__main__':
    customers, transactions, promotions = load_data()
    print("Customers:", customers.shape)
    print("Transactions:", transactions.shape)
    print("Promotions:", promotions.shape)
    print("\nSample Customers:")
    print(customers.head(3))
    customers.to_csv('data/customers.csv', index=False)
    transactions.to_csv('data/transactions.csv', index=False)
    promotions.to_csv('data/promotions.csv', index=False)
    print("\nCSV files saved to data/ folder!")