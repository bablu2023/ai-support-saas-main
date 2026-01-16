from rest_framework.decorators import api_view
from rest_framework.response import Response
from billing.models import Plan, Payment
from billing.services.razorpay_service import create_order, verify_signature
from organizations.models import Organization

@api_view(["POST"])
def create_payment(request):
    org = Organization.objects.get(id=request.data["org_id"])
    plan = Plan.objects.get(id=request.data["plan_id"])

    order = create_order(plan.price)

    Payment.objects.create(
        organization=org,
        plan=plan,
        razorpay_order_id=order["id"]
    )

    return Response({
        "order_id": order["id"],
        "amount": plan.price,
        "key": os.getenv("RAZORPAY_KEY_ID"),
    })


@api_view(["POST"])
def verify_payment(request):
    data = request.data

    verify_signature({
        "razorpay_order_id": data["razorpay_order_id"],
        "razorpay_payment_id": data["razorpay_payment_id"],
        "razorpay_signature": data["razorpay_signature"],
    })

    payment = Payment.objects.get(
        razorpay_order_id=data["razorpay_order_id"]
    )

    payment.status = "paid"
    payment.razorpay_payment_id = data["razorpay_payment_id"]
    payment.razorpay_signature = data["razorpay_signature"]
    payment.save()

    # 🔥 Upgrade plan
    org = payment.organization
    org.plan = payment.plan
    org.save()

    return Response({"status": "success"})
