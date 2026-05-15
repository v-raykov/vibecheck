from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Vibe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vibes")
    percentage = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    emoji = models.CharField(max_length=10)
    content = models.CharField(max_length=140, blank=True, null=True)
    likes = models.ManyToManyField(User, through='VibeLike', related_name="liked_vibes", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    track_id = models.CharField(max_length=100, blank=True, null=True)

    snippet_start = models.PositiveIntegerField(blank=True, null=True,
                                                validators=[MinValueValidator(0)])
    snippet_end = models.PositiveIntegerField(blank=True, null=True,
                                              validators=[MinValueValidator(1)])

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(snippet_end__gt=models.F('snippet_start')) |
                          models.Q(snippet_start__isnull=True) |
                          models.Q(snippet_end__isnull=True),
                name='snippet_end_greater_than_start_if_present'
            )
        ]

    def clean(self):
        super().clean()
        if self.track_id:
            if self.snippet_start is None or self.snippet_end is None:
                raise ValidationError("Both start and end timestamps are required if a music track is selected.")
            if self.snippet_end <= self.snippet_start:
                raise ValidationError({'snippet_end': 'The snippet end time must be after the start time.'})
            if self.snippet_end - self.snippet_start > 30:
                raise ValidationError('Snippets cannot be longer than 30 seconds.')
        else:
            self.snippet_start = None
            self.snippet_end = None

    def __str__(self):
        if self.track_id:
            return f"{self.user.username}'s vibe - Track {self.track_id} ({self.snippet_start}s-{self.snippet_end}s)"
        return f"{self.user.username}'s vibe - Text Only"


class VibeLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vibe = models.ForeignKey(Vibe, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'vibe'],
                name='unique_user_vibe_like'
            )
        ]
