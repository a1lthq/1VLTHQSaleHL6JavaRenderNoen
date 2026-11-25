import os
import uuid
from datetime import date
import psycopg
from psycopg.rows import dict_row

def connect():
    url = os.environ['DATABASE_URL'].strip()
    return psycopg.connect(url, row_factory=dict_row, connect_timeout=10)

def load_categories():
    with connect() as conn:
        return conn.execute('SELECT trim(msnhom) AS id, tennhom AS name FROM public.nhommh ORDER BY msnhom').fetchall()

PRODUCT = 'SELECT trim(msmh) AS id, tenmh AS name, gia AS price, mota AS description, hinh AS image, trim(msnhom) AS category_id, size FROM public.mh'

def load_products(category_id=None, kw=None):
    sql = PRODUCT + ' WHERE gia IS NOT NULL AND gia >= 0'
    args = []
    if category_id:
        sql += ' AND msnhom = %s'; args.append(category_id)
    if kw:
        sql += ' AND tenmh ILIKE %s'; args.append('%'+kw+'%')
    with connect() as conn:
        return conn.execute(sql+' ORDER BY msmh', args).fetchall()

def get_product_by_id(product_id):
    with connect() as conn:
        return conn.execute(PRODUCT+' WHERE msmh = %s', (product_id,)).fetchone()

def add_order(cart, name, address, phone, note):
    customer_id = uuid.uuid4().hex[:20]
    order_id = uuid.uuid4().hex[:20]
    with connect() as conn:
        # Do not merge customer records by phone: no uniqueness/authentication in original schema.
        conn.execute('INSERT INTO public.kh (mskh, tenkh, dc, soll, diem) VALUES (%s,%s,%s,%s,0)', (customer_id,name,address,phone))
        conn.execute('INSERT INTO public.ddh (msddh, ngaylap, mskh, nguoinhan, dcgiao, sollnhan, tinhtrang, ghichu) VALUES (%s,%s,%s,%s,%s,%s,false,%s)', (order_id,date.today(),customer_id,name,address,phone,note))
        for pid, qty in cart.items():
            product = conn.execute('SELECT gia FROM public.mh WHERE msmh=%s', (pid,)).fetchone()
            if not product or product['gia'] is None or product['gia'] < 0 or not 1 <= qty <= 99:
                raise ValueError('Sản phẩm hoặc số lượng không hợp lệ')
            conn.execute('INSERT INTO public.ctddh (msddh,msmh,sl) VALUES (%s,%s,%s)',(order_id,pid,qty))
    return order_id
