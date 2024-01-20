import os
from flask import Flask, redirect, request
import stripe


# This is your test secret API key.
stripe.api_key = 'sk_test_51OPSVaIGppHzuUaIImziYC43tisQhhhwNwjgcFtY1yltxTHYQrQRykjkHpBpGEHaUwmAH7Dbb3RwhuhZhMqztw1S00d7rsLUVF'
"""from flask import Flask, render_template

app = Flask(__name__)

app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51OPSVaIGppHzuUaIIJsjb08I1RVMYwSN1IinmZ5TcUrqhi1xSlFnDAlbW1hw046EfdSnCvneXtf6n3hVvFfTcDgX00WfET7pNV'
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51OPSVaIGppHzuUaIImziYC43tisQhhhwNwjgcFtY1yltxTHYQrQRykjkHpBpGEHaUwmAH7Dbb3RwhuhZhMqztw1S00d7rsLUVF'


@app.route("/")
def checkout():
    return render_template("checkout.html")


if __name__ == "__main__":
    app.run()
"""


app = Flask(__name__,
            static_url_path='',
            static_folder='public')

YOUR_DOMAIN = 'http://localhost:4242'


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': '{{PRICE_ID}}',
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/successfultrans.html',
            cancel_url=YOUR_DOMAIN + '/cancel.html',
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)


if __name__ == '__main__':
    app.run(port=4242)
