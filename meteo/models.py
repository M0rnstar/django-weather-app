from django.db import models

from django.db import models

class SearchLog(models.Model):
    city = models.CharField(max_length=100)
    count = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.city}: {self.count}"