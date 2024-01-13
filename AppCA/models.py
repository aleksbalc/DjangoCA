from django.db import models
from django.utils.timezone import now

class KeyGeneration(models.Model):
    created_at = models.DateTimeField(default=now, editable=False)
    number_of_keys_created = models.IntegerField(default=0)

class Node(models.Model):
    N_ID = models.CharField(max_length=4)
    NTAG = models.CharField(max_length=32, default='')
    NNSK = models.CharField(max_length=16, default='')
    NNSKiv = models.CharField(max_length=16, default='')
    NNSKsign = models.CharField(max_length=16, default='')
    HMAC = models.CharField(max_length=64, default='')  # Assuming HMAC is a SHA256 hash (64 characters)

    # New columns
    device_id = models.CharField(max_length=17, default='')  # Assuming MAC addresses are 17 characters long
    generation_id = models.ForeignKey(KeyGeneration, on_delete=models.CASCADE, default=None)

    # Node state
    STATE_CHOICES = [
        ('unknown', 'Unknown'),
        ('requires_key', 'Requires Key'),
        ('ready_to_register', 'Ready to Register'),
        ('registered', 'Registered'),
    ]
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='unknown')

    def __str__(self):
        return f"Node {self.N_ID} - {self.get_state_display()}"
