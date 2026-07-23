import uuid

from django.db import models


class UUIDModel(models.Model):
    # UUID primary key, safe to expose and collision-free across systems
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
