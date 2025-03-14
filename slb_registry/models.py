from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.timezone import now
from device_inventory.models import DeviceInfo
import uuid


class DeploymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    ROLLED_BACK = 'rolled_back', 'Rolled Back'

class DeploymentTransaction(models.Model):
    """Tracks configuration deployments to F5 devices"""
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    frontend_handle = models.ForeignKey(
        'FrontendInfo',
        on_delete=models.CASCADE,
        related_name='deployments'
    )
    device_fqdn = models.ForeignKey(
        DeviceInfo,
        on_delete=models.RESTRICT,
        related_name='deployments',
        limit_choices_to={'device_platform_vendor': 'f5', 'object_db_status': 'active'}
    )
    status = models.CharField(
        max_length=20,
        choices=DeploymentStatus.choices,
        default=DeploymentStatus.PENDING
    )
    config_snapshot = models.JSONField(help_text="Configuration snapshot at deployment time")
    error_message = models.TextField(null=True, blank=True)
    created_by = models.EmailField()
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_id} - {self.frontend_handle} - {self.status}"

class DeploymentLog(models.Model):
    """Detailed logs for deployment transactions"""
    log_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    deployment = models.ForeignKey(
        DeploymentTransaction,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    timestamp = models.DateTimeField(default=now)
    log_level = models.CharField(
        max_length=10,
        choices=[
            ('INFO', 'Info'),
            ('WARNING', 'Warning'),
            ('ERROR', 'Error')
        ]
    )
    message = models.TextField()
    detail = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

class HealthCheckInfo(models.Model):
    healthcheck_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    healthcheck_handle = models.CharField(max_length=50, primary_key=True)
    HEALTHCHECK_TYPES = {
        "tcp": "tcp",
        "http": "http",
        "https": "https",
        "mysql": "mysql",
    }

    device_fqdn = models.ForeignKey(
        DeviceInfo,
        to_field="device_fqdn",
        on_delete=models.RESTRICT,
        default="placeholder",
        null=True,
        blank=True,
    )
    healthcheck_type = models.CharField(
        max_length=20, choices=HEALTHCHECK_TYPES, null=False, blank=False, default="tcp"
    )
    interval = models.PositiveIntegerField(help_text="Check interval in seconds")
    timeout = models.PositiveIntegerField(help_text="Timeout in seconds")
    send_string = models.CharField(max_length=255, help_text="String to send")
    receive_string = models.CharField(max_length=255, help_text="Expected response")
    healthcheck_port = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(65535)],
    )
    object_db_status = models.CharField(max_length=10, default="active")


class BackendInfo(models.Model):
    backend_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    backend_handle = models.SlugField(max_length=50, primary_key=True)
    device_fqdn = models.ForeignKey(
        DeviceInfo,
        to_field="device_fqdn",
        on_delete=models.RESTRICT,
        limit_choices_to={"object_db_status": "active"},
        default="placeholder",
        null=True,
        blank=True,
    )
    load_balancing_mode = models.CharField(max_length=20)
    healthcheck_handle = models.ForeignKey(
        HealthCheckInfo, to_field="healthcheck_handle", on_delete=models.SET_NULL, null=True, blank=True
    )
    first_discovery_datetime = models.DateTimeField(default=now, blank=True)
    last_update_datetime = models.DateTimeField(default=now, blank=True)
    object_db_status = models.CharField(max_length=10, default="active")


class BackendMembers(models.Model):
    backend_handle = models.ForeignKey(
        BackendInfo, on_delete=models.CASCADE, related_name="members"
    )
    ip_address = models.GenericIPAddressField()
    port = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(65535)],
    )
    weight = models.PositiveIntegerField(default=1)
    priority = models.PositiveIntegerField(default=0)
    admin_state = models.BooleanField(default="enabled")
    health_status = models.CharField(max_length=10, default="available")

    class Meta:
        unique_together = ["backend_handle", "ip_address", "port"]

    def __str__(self):
        return f"{self.ip_address}:{self.port}"


# class SlbVIP(models.Model):
#     handle = models.SlugField(max_length=50, primary_key=True, unique=True)
#     address = models.CharField(max_length=128)
#     address_type = models.CharField(max_length=4)
#     port = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(65535)],)
#     protocol = models.CharField(max_length=5)
#     pool_name = models.SlugField(max_length=50, default='')
#     connection_type = models.CharField(max_length=20)
#     admin_state = models.CharField(max_length=10)
#     platform_vendor = models.CharField(max_length=10)
#     slb_name = models.CharField(max_length=50)
#     datacenter = models.CharField(max_length=10)
#     security_zone = models.CharField(max_length=10, default='')
#     devhub_id = models.IntegerField(default=0)
#     devhub_app_slug = models.CharField(max_length=20)
#     team_distro = models.CharField(max_length=900, validators=[EmailValidator()])


class FrontendInfo(models.Model):

    ADDRESS_TYPES = {"ipv4": "ipv4", "ipv6": "ipv6"}
    L4_PROTOCOLS = {"tcp": "tcp", "udp": "udp"}
    CONNECTION_TYPES = {"full_proxy": "full_proxy", "half_proxy": "half_proxy"}

    frontend_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    frontend_handle = models.SlugField(max_length=50, primary_key=True)
    listener_address = models.CharField(max_length=39)  # based on ipv6 address type
    address_type = models.CharField(max_length=4, choices=ADDRESS_TYPES)
    port = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(65535)],
    )
    protocol = models.CharField(max_length=5, choices=L4_PROTOCOLS)
    backend_handle = models.ForeignKey(
        BackendInfo,
        to_field="backend_handle",
        on_delete=models.RESTRICT,
        limit_choices_to={"object_db_status": "active"},
        null=True,
        blank=True,
    )
    connection_type = models.CharField(
        max_length=20, choices=CONNECTION_TYPES
    )  # full proxy vs half proxy
    admin_state = models.CharField(max_length=10)
    device_fqdn = models.ForeignKey(
        DeviceInfo,
        to_field="device_fqdn",
        on_delete=models.RESTRICT,
        limit_choices_to={"object_db_status": "active"},
        default="placeholder",
        null=False,
        blank=False,
    )
    datacenter = models.CharField(max_length=10, null=False, blank=True)
    security_zone = models.CharField(max_length=10, null=False, blank=True)
    app_inventory_id = models.IntegerField(default=0)
    app_inventory_slug = models.CharField(max_length=30)
    team_distro = models.CharField(max_length=90, validators=[EmailValidator()])
    first_discovery_datetime = models.DateTimeField(default=now)
    last_update_datetime = models.DateTimeField(default=now)
    object_db_status = models.CharField(max_length=10, default="active")


@receiver(pre_save, sender=FrontendInfo)
def fill_datacenter_zone(sender, instance, **kwargs):

    print(instance)
    # if instance.device_fqdn and not instance.datacenter:
    instance.datacenter = instance.device_fqdn.device_datacenter


@receiver(pre_save, sender=FrontendInfo)
def fill_security_zone(sender, instance, **kwargs):
    if instance.device_fqdn and not instance.security_zone:
        instance.security_zone = instance.device_fqdn.device_security_zone

