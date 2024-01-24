from django.db import models
from django.utils.timezone import now

class KeyGeneration(models.Model):
    created_at = models.DateTimeField(default=now, editable=False)
    number_of_keys_created = models.IntegerField(default=0)

class Node(models.Model):
    N_ID = models.CharField(max_length=4, unique=True)
    NTAG = models.CharField(max_length=32, default='', blank=True)
    HMAC = models.CharField(max_length=64, default='', blank=True)  # Assuming HMAC is a SHA256 hash (64 characters)

    # New columns
    device_id = models.CharField(max_length=17, default='', blank=True)  # Assuming MAC addresses are 17 characters long
    key_set_id = models.ForeignKey(KeyGeneration, on_delete=models.CASCADE, default=None)

    # Node state
    STATE_CHOICES = [
        ('id ready', 'ID ready'),
        ('credentials available', 'Credentials available'),
        ('credentials taken ', 'Credentials taken'),
        ('unknown', 'Unknown'),
    ]
    state = models.CharField(max_length=32, choices=STATE_CHOICES, default='unknown')

    def __str__(self):
        return f"Node {self.N_ID} - {self.get_state_display()}"

class KeyRequests(models.Model):
    client_name = models.CharField(max_length=16)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_id = models.CharField(max_length=17, default='')
    created_at = models.DateTimeField(default=now, editable=False)

    def __str__(self):
        return f"Key Request - IP: {self.ip_address}, Device ID: {self.device_id}"
