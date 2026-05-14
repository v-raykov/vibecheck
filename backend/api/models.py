from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Vibe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vibes")
    percentage = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    emoji = models.CharField(max_length=10)
    content = models.CharField(max_length=140, blank=True, null=True)
    likes = models.ManyToManyField(User, through='VibeLike', related_name="liked_vibes", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.percentage}%"

class VibeLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vibe = models.ForeignKey(Vibe, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'vibe')