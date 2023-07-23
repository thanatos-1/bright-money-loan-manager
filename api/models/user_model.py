from django.db import models

from utils.slug_util import slugify



class User(models.Model):
    slug = models.SlugField(blank=True, null=True, unique=True)
    username = models.CharField(max_length=255, blank=False, null=False)
    aadhar_id = models.CharField(max_length=255, blank=False, null=False, unique=True)
    email = models.EmailField(max_length=255, blank=False, null=False)
    annual_income = models.IntegerField(blank=False, null=False)
    total_balance = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=12)
    credit_score = models.IntegerField(blank=True, default=0, null=False)

    class Meta:
        managed = True
        db_table = "user_model"

    def __str__(self) -> str:
        return f"{self.username}_{self.email}_{self.credit_score}"
    
    def save(self, *args, **kwargs) -> None:
        if not self.id:
            super(User, self).save(*args, **kwargs)
            self.slug = slugify(self.id)
            self.save()
            return
        super(User, self).save(*args, **kwargs)
    
