from werkzeug.security import generate_password_hash
import csv
from faker import Faker
import datetime

num_users = 100
num_products = 100
num_purchases = 2500

Faker.seed(0)
fake = Faker()


def get_csv_writer(f):
    return csv.writer(f, dialect='unix')


def gen_users(num_users):
    with open('Users.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Users...', end=' ', flush=True)
        for uid in range(num_users):
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            profile = fake.profile()
            email = profile['mail']
            plain_password = f'pass{uid}'
            password = generate_password_hash(plain_password)
            name = profile['name']
            address = fake.address()
            balance = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
            writer.writerow([uid, email, password, name, address, balance])
        print(f'{num_users} generated')
    return


def gen_products(num_products):
    available_pids = []
    with open('Products.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)
        for pid in range(num_products):
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            name = fake.sentence(nb_words=4)[:-1]
            image = 0
            category = fake.random_element(elements=('Cosmetics', 'Electronics', 'Home Goods', 'Food'))
            price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
            description = fake.sentence(nb_words=10)[:-1]
            writer.writerow([pid, image, category, name, price, description])
        print(f'{num_products} generated; {len(available_pids)} available')
    return available_pids


def gen_inventory(num_purchases):
    with open('Inventory.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Inventory...', end=' ', flush=True)
        for id in range(num_purchases):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            sid = fake.random_int(min=0, max=num_users-1)
            pid = fake.random_int(min=0, max=num_products-1)
            quantity = fake.random_int(max=30)
            writer.writerow([sid, pid, quantity])
        print(f'{num_purchases} generated')
    return

def gen_sellers(num_users):
    with open("Sellers.csv", "w") as f:
        writer = get_csv_writer(f)
        print('Seller...', end=' ', flush=True)
        for id in range(20):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            pid = fake.random_int(max=num_users-1)
            writer.writerow([pid])
    return

def gen_purchaes(num_purchases):
    with open('Purchases.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Purchases...', end=' ', flush=True)
        for id in range(num_purchases):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            uid = fake.random_int(min=0, max=num_users-1)
            pid = fake.random_int(min=0, max=num_products-1)
            date = fake.date_this_month().strftime('%s')
            writer.writerow([id, pid, uid, date])
        print(f'{num_purchases} generated')

def gen_cart():
    with open('Cart.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Cart...', end=' ', flush=True)
        for id in range(30):
            # Update to select from sellers
            uid = fake.random_int(min=0, max=num_users-1)
            pid = fake.random_int(min=0, max=num_products-1)
            sid = fake.random_int(min=0, max=num_users-1)
            quantity = fake.random_int(max=20)
            writer.writerow([quantity, uid, pid, sid])


def gen_rates(filename):
    with open(filename, 'w') as f:
        writer = get_csv_writer(f)
        print(filename, end=' ', flush=True)
        for num in range(30):
            fid = fake.random_int(min=0, max=num_users-1)
            uid = fake.random_int(min=0, max=num_users-1)
            dates = fake.date_this_month().strftime('%s')
            rating = fake.random_int(min=1, max=5)
            review = fake.sentence(nb_words=40)[:-1]
            writer.writerow([fid, uid, dates, rating, review])

def gen_orders():
    with open("Orders.csv", 'w') as f:
        writer = get_csv_writer(f)
        print("Orders...", end=' ', flush=True)
        for oid in range(30):
            # Update sid to select from sellers
            sid = fake.random_int(min=0, max=num_users-1)
            uid = fake.random_int(min=0, max=num_users-1)
            pid = fake.random_int(min=0, max=num_products-1)
            dates = fake.date_this_month().strftime('%s')
            quantity = fake.random_int(min=0, max = 20)
            rating = fake.random_int(min=1, max=5)
            fufilled = fake.random_element(elements=('true', 'false'))
            price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
            writer.writerow([oid, sid, uid, quantity, dates, fufilled, price])




gen_users(num_users)
gen_products(num_products)
gen_inventory(num_purchases)
gen_sellers(num_users)
gen_purchaes(num_purchases)
gen_rates("RatesSeller.csv")
gen_rates("RatesProduct.csv")
gen_orders()
gen_cart()

