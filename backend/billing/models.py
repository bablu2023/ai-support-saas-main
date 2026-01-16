from django.db import models


class Plan(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField()  # INR
    monthly_token_limit = models.IntegerField()

    def __str__(self):
        return self.name


class TokenUsage(models.Model):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="token_usages",
    )
    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)
    total_tokens = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class Payment(models.Model):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
    )
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)

    razorpay_order_id = models.CharField(max_length=255)
    razorpay_payment_id = models.CharField(max_length=255, blank=True)
    razorpay_signature = models.CharField(max_length=255, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ("created", "Created"),
            ("paid", "Paid"),
            ("failed", "Failed"),
        ],
        default="created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
