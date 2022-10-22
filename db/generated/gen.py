from werkzeug.security import generate_password_hash
import csv
from faker import Faker
import datetime

num_users = 100
num_products = 100
num_purchases = 2500
inventory = 50

Faker.seed(0)
fake = Faker()


def get_csv_writer(f):
    return csv.writer(f, dialect='unix')


def gen_users():
    users = set()
    with open('./db/data/Users.csv', 'w') as f:
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
            users.add(uid)
            writer.writerow([uid, email, password, name, address, balance])
        print(f'{num_users} generated')
    return users


def gen_products():
    products = set()
    with open('./db/data/Products.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)
        for pid in range(num_products):
            products.add(pid)
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            name = fake.sentence(nb_words=4)[:-1]
            image = 0
            category = fake.random_element(elements=('Cosmetics', 'Electronics', 'Home Goods', 'Food'))
            price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
            description = fake.sentence(nb_words=10)[:-1]
            writer.writerow([pid, image, category, name, price, description])
        print(f'{num_products} generated;')
    return products

def gen_sellers():
    sellers = set()
    with open("./db/data/Sellers.csv", "w") as f:
        writer = get_csv_writer(f)
        print('Seller...', end=' ', flush=True)
        for id in range(20):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            sid = fake.random_int(max=num_users-1)
            while sid in sellers:
                sid = fake.random_int(max=num_users-1)
            sellers.add(sid)
            writer.writerow([sid])
    return sellers

def gen_inventory(sellers, products):
    with open('./db/data/Inventory.csv', 'w') as f:
        writer = get_csv_writer(f)
        used_keys = set()
        print('Inventory...', end=' ', flush=True)
        for id in range(inventory):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            sid = fake.random_element(elements=list(sellers))
            pid = fake.random_element(elements=list(products))
            while (sid, pid) in used_keys:
                sid = fake.random_element(elements=list(sellers))
                pid = fake.random_element(elements=list(products))
            used_keys.add((sid, pid))
            # print(sid, pid)
            quantity = fake.random_int(max=30)
            writer.writerow([sid, pid, quantity])
        print(f'{num_products} generated')
    return

def gen_purchases(users, products):
    with open('./db/data/Purchases.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Purchases...', end=' ', flush=True)
        for id in range(num_purchases):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            uid = fake.random_element(elements=list(users))
            pid = fake.random_element(elements=list(products))
            date = fake.date_time_this_month().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([id, uid, pid, date])
        print(f'{num_purchases} generated')

def gen_cart(users, products, sellers):
    combos = set()
    with open('./db/data/Cart.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Cart...', end=' ', flush=True)
        for id in range(30):
            # Update to select from sellers
            uid = fake.random_element(elements=list(users))
            pid = fake.random_element(elements=list(products))
            sid = fake.random_element(elements=list(sellers))
            while (uid, pid, sid) in combos:
                uid = fake.random_element(elements=list(users))
                pid = fake.random_element(elements=list(products))
                sid = fake.random_element(elements=list(sellers))
            combos.add((uid, pid, sid))
            quantity = fake.random_int(max=20)
            writer.writerow([quantity, uid, pid, sid])


def gen_rates(filename, people, users):
    combo = set()
    with open(filename, 'w') as f:
        writer = get_csv_writer(f)
        print(filename, end=' ', flush=True)
        for num in range(30):
            fid = fake.random_element(elements=people)
            uid = fake.random_element(elements=users)
            while (fid, uid) in combo:
                fid = fake.random_element(elements=people)
                uid = fake.random_element(elements=users)
            dates = fake.date_time_this_month().strftime("%Y-%m-%d %H:%M:%S")
            rating = fake.random_int(min=1, max=5)
            review = fake.sentence(nb_words=40)[:-1]
            writer.writerow([fid, uid, dates, rating, review])

def gen_orders(sellers, users, products):
    with open("./db/data/Orders.csv", 'w') as f:
        writer = get_csv_writer(f)
        print("Orders...", end=' ', flush=True)
        for oid in range(30):
            # Update sid to select from sellers
            sid = fake.random_element(elements=sellers)
            uid = fake.random_element(elements=users)
            pid = fake.random_element(elements=products)
            dates = fake.date_time_this_month().strftime("%Y-%m-%d %H:%M:%S")
            quantity = fake.random_int(min=0, max = 20)
            rating = fake.random_int(min=1, max=5)
            fufilled = fake.random_element(elements=('true', 'false'))
            price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
            writer.writerow([oid, sid, uid, pid, quantity, dates, fufilled, price])




users = gen_users()
products = gen_products()
sellers = gen_sellers()
gen_inventory(sellers, products)
gen_purchases(users, products)
gen_rates("./db/data/RatesSeller.csv", sellers, users)
gen_rates("./db/data/RatesProduct.csv", products, users)
gen_orders(sellers, users, products)
gen_cart(users, products, sellers)

