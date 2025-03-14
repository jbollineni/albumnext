"""
Device Inventory Model
"""

import uuid
from django.db import models

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.timezone import now


# Create your models here.
class DeviceInfo(models.Model):
    device_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    device_fqdn = models.CharField(max_length=50, unique=True, primary_key=True)
    DEVICE_STATUS = {
        "active": "active",
        "decommissioned": "decommissioned",
        "designated": "designated",
    }
    PLATFORM_VENDORS = {"f5": "f5", "haproxy": "haproxy"}
    DATACENTERS = {"ashburn": "ashburn", "chicago": "chicago", "hillsboro": "hillsboro"}
    SECURITY_ZONES = {
        "internal": "Green (Internal)", 
        "dmz": "Blue (DMZ / Internet or Partner Facing)",
        "sensitive": "Black (Sensitive)",
        "office": "Red (Office)",
        "none": "none"
        }

    PLATFORM_ROLES = {"slb_shared": "SLB Shared", "slb_private_gw": "SLB Private Gateway", "GSLB": "GSLB"}

    device_platform_vendor = models.CharField(
        max_length=10, choices=PLATFORM_VENDORS, null=False, blank=False
    )
    cluster_primary_unit = models.CharField(max_length=50)
    cluster_secondary_unit = models.CharField(max_length=50, default="")
    cluster_tertiary_unit = models.CharField(max_length=50, default="")
    cluster_quaternary_unit = models.CharField(max_length=50, default="")
    device_datacenter = models.CharField(
        max_length=10, choices=DATACENTERS, null=False, blank=False, default="ashburn"
    )
    device_security_zone = models.CharField(
        max_length=10, choices=SECURITY_ZONES, null=True, blank=True, default="none"
    )
    # device_admin_state = models.CharField(
    #     max_length=10, choices=ADMIN_STATES, null=False, blank=False
    # )
    object_db_status = models.CharField(
        default="active", choices=DEVICE_STATUS, null=False, blank=False
    )
    device_role = models.CharField(
        max_length=20, choices=PLATFORM_ROLES, null=False, blank=False, default="none"
    )
    device_capabilities = models.CharField(max_length=50, default="")
    first_discovery_datetime = models.DateTimeField(default=now)

    # def save(self, *args, **kwargs):
    #     self.device_fqdn = self.cluster_primary_unit
    #     super().save(*args, **kwargs)


@receiver(pre_save, sender=DeviceInfo)
def update_device_fqdn(sender, instance, **kwargs):
    instance.device_fqdn = instance.cluster_primary_unit