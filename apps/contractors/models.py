from django.db import models
from apps.auth.models import ContractorProfile

class ContractorReview(models.Model):
    contractor = models.ForeignKey(ContractorProfile, on_delete=models.CASCADE, related_name='reviews')
    rating = models.FloatField()
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.contractor.user.username}: {self.rating}" 