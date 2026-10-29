from django.db import models


class Order(models.Model):
    """The object whose save() fires post_save (used in the Q3 proof)."""

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class AuditLog(models.Model):
    """Row written by the post_save receiver (used in the Q3 proof)."""

    message = models.CharField(max_length=200)

    def __str__(self):
        return self.message
