from flask import Flask, request, redirect, jsonify
import stripe
import json
import os

app = Flask(__name__)

# Use environment variable for secret key to avoid exposing it in public code
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Use environment variable for price id
PRICE_ID = os.environ.get('STRIPE_PRICE_ID')

# Local path to user database (in Render you'll probably use persistent volume or cloud storage in future)
USER_DB_PATH = 'users.json'

@app.route('/create-checkout-session')
def create_checkout_session():
    email = request.args.get('email')
    if not email:
        return "Missing email", 400

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='subscription',
            line_items=[{
                'price': PRICE_ID,
                'quantity': 1,
            }],
            customer_email=email,
            success_url='https://farooqi-payments.onrender.comsuccess?email=' + email,
            cancel_url='https://farooqi-payments.onrender.com/cancel',

        )
        return redirect(session.url, code=303)
    except Exception as e:
        return str(e), 500

@app.route('/success')
def success():
    email = request.args.get('email')
    if not email:
        return "Missing email", 400

    if os.path.exists(USER_DB_PATH):
        with open(USER_DB_PATH, 'r') as f:
            data = json.load(f)
    else:
        data = {}

    user = data.get(email, {})
    user['email'] = email
    user['is_premium'] = True
    data[email] = user

    with open(USER_DB_PATH, 'w') as f:
        json.dump(data, f, indent=2)

    return "<h1>Payment successful ✅</h1><p>You can now close this window.</p>"

@app.route('/cancel')
def cancel():
    return "<h1>Payment cancelled</h1>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 4242))
    app.run(host='0.0.0.0', port=port)
