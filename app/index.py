import secrets
from pathlib import PurePosixPath, Path
from flask import render_template, request, session, redirect, url_for, abort, jsonify
from app import app, dao

@app.context_processor
def common():
    return dict(categories=dao.load_categories(), cart_count=sum(session.get('cart', {}).values()), csrf=csrf_token())

def csrf_token():
    if 'csrf' not in session: session['csrf']=secrets.token_hex(24)
    return session['csrf']

@app.before_request
def protect():
    if request.method == 'POST' and not secrets.compare_digest(request.form.get('csrf',''), session.get('csrf','') or '!'):
        abort(400)

@app.template_filter('product_image')
def product_image(path):
    name=PurePosixPath((path or '').replace('\\','/').strip()).name
    if name and (Path(app.static_folder)/'images'/name).is_file():
        return url_for('static',filename='images/'+name)
    return url_for('static',filename='images/placeholder.svg')

@app.get('/')
def index():
    return render_template('index.html', products=dao.load_products(request.args.get('category_id'),request.args.get('keyword')))

@app.get('/products/<product_id>')
def detail(product_id):
    p=dao.get_product_by_id(product_id)
    if not p: abort(404)
    return render_template('details.html',product=p)

@app.get('/cart')
def cart():
    rows=[]
    for pid, qty in session.get('cart',{}).items():
        p=dao.get_product_by_id(pid)
        if p and p['price'] is not None: rows.append(dict(p,quantity=qty))
    return render_template('cart.html',rows=rows,total=sum(p['price']*p['quantity'] for p in rows))

@app.post('/cart/<product_id>')
def cart_change(product_id):
    items=dict(session.get('cart',{}))
    action=request.form.get('action')
    if action=='remove': items.pop(product_id,None)
    else:
        p=dao.get_product_by_id(product_id)
        if not p or p['price'] is None or p['price'] < 0: abort(404)
        if action=='add':
            if product_id not in items and len(items)>=30: abort(400)
            items[product_id]=min(99,items.get(product_id,0)+1)
        elif action=='update' and product_id in items:
            qty=request.form.get('quantity',type=int)
            if qty is None or not 1<=qty<=99: abort(400)
            items[product_id]=qty
        else: abort(400)
    session['cart']=items
    return redirect(url_for('cart'))

@app.post('/pay')
def pay():
    items=session.get('cart',{})
    name=request.form.get('name','').strip(); address=request.form.get('address','').strip(); phone=request.form.get('phone','').strip(); note=request.form.get('note','').strip()
    if not items or not 1<=len(name)<=150 or not 1<=len(address)<=250 or not 1<=len(phone)<=15 or len(note)>550:
        return 'Thông tin đặt hàng không hợp lệ',400
    try: order_id=dao.add_order(items,name,address,phone,note)
    except ValueError: return 'Giỏ hàng không hợp lệ',400
    session.pop('cart',None)
    return render_template('success.html',order_id=order_id)

@app.get('/health')
def health():
    with dao.connect() as conn: conn.execute('SELECT 1')
    return jsonify(status='ok')
