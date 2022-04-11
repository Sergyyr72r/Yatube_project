from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class post (models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )


