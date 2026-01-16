import razorpay
import os

client = razorpay.Client(
    auth=(
        os.getenv("RAZORPAY_KEY_ID"),
        os.getenv("RAZORPAY_KEY_SECRET"),
    )
)

def create_order(amount):
    return client.order.create({
        "amount": amount * 100,  # INR → paise
        "currency": "INR",
        "payment_capture": 1
    })

def verify_signature(data):
    client.utility.verify_payment_signature(data)
