from django.db import models
from authentication.models import User

# Create your models here.
class Expense(models.Model):
    SOURCE_OPTIONS = [
        ('SALARY','SALARY'),
        ('BUSINESS','BUSINESS'),
        ('SIDE-HUSTLES','FOOD'),
        ('OTHERS','OTHERS'),
    ]
    source=models.CharField(choices=SOURCE_OPTIONS,max_length=255)
    amount=models.DecimalField(max_digits=10,decimal_places=2,max_length=255)
    description=models.TextField()
    owner=models.ForeignKey(to=User,on_delete=models.CASCADE)
    date=models.DateField(null=False,blank=False)
    

    class Meta:
        ordering: '-date'

    def __str__(self) -> str:
        return str(self.owner)+'s income'
