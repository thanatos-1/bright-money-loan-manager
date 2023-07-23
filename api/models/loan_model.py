from django.db import models

from utils.slug_util import slugify
from .user_model import User
from api.constants import LoanType



class LoanModel(models.Model):
    slug = models.SlugField(blank=True, null=True, unique=True)
    user = models.ForeignKey("User", null=False, on_delete=models.CASCADE, related_name="loan")
    loan_type = models.CharField(max_length=100, null=False, blank=False, choices=LoanType.choices)
    loan_amount = models.IntegerField(null=False, blank=False)
    interest_rate = models.DecimalField(null=False, blank=False, decimal_places=2, max_digits=12)
    term_period = models.IntegerField(null=False, blank=False)
    disbursement_date = models.DateField(null=False, blank=False)
    
    last_payment_date = models.DateField(null=True)
    next_payment_date = models.DateField(null=True)
    current_emi = models.DecimalField(null=True, decimal_places=2, max_digits=12)
    current_due = models.DecimalField(null=True, decimal_places=2, max_digits=12)
    principal_due_monthly = models.DecimalField(null=True, decimal_places=2, max_digits=12)
    current_paid = models.DecimalField(null=True, default=0, decimal_places=2, max_digits=12)
    total_emi = models.IntegerField(null=True, default=0)
    
    class Meta:
        managed = True
        db_table = "loan_table"

    def __str__(self) -> str:
        return f"{self.slug}_{self.loan_amount}_{self.loan_amount}_{self.interest_rate}_{self.term_period}"
    
    def save(self, *args, **kwargs):
        if not self.id:
            super(User, self).save(*args, **kwargs)
            self.slug = slugify(self.id)
            self.save()
            return
        super(User, self).save(*args, **kwargs)


class LoanTransaction(models.Model):
    slug = models.SlugField(blank=True, null=True, unique=True)
    date_due = models.DateField(null=False)
    date_paid = models.DateField(null=False)
    principal = models.DecimalField(null=False, decimal_places=2, max_digits=12)
    interest = models.DecimalField(null=False, decimal_places=2, max_digits=12)
    amount_paid = models.DecimalField(null=False, decimal_places=2, max_digits=12)
    loan = models.ForeignKey("LoanModel",null=False, on_delete=models.CASCADE, related_name="transaction")
    
    class Meta:
        managed = True
        db_table = "transaction_table"

    def __str__(self) -> str:
        return f"{self.slug}_{self.amount_paid}"
    
    def save(self, *args, **kwargs):
        if not self.id:
            super(User, self).save(*args, **kwargs)
            self.slug = slugify(self.id)
            self.save()
            return 
        super(User, self).save(*args, **kwargs)