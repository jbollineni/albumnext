from django import forms
from crispy_forms.helper import FormHelper
from django.utils.safestring import mark_safe
from crispy_forms.layout import Layout, Row, Column, Field, Div, HTML, ButtonHolder, Submit
from crispy_forms.bootstrap import InlineRadios, AccordionGroup, Accordion, PrependedText, AppendedText, StrictButton, FieldWithButtons
from django.forms import formset_factory
from django.utils.safestring import mark_safe


class SlbCreateForm(forms.Form):

    # Admin Information
    APP_INVENTORY_SLUG = forms.ChoiceField(
        required=True,
        label="Devhub Application Slug",
        choices=[
            ("convoy", "Convoy"),
            ("einstein", "Einstein"),
            ("bbdevops", "Backbone-DevOps"),
        ],
        help_text="Select the coresponding Devhub application name",
    )
    TEAM_DISTRO_LIST = forms.EmailField(
        required=True,
        label="Team Distribution List",
        initial="team@comcast.net",
        widget=forms.EmailInput(attrs={'class': 'textinput form-control'}),
        help_text="Must be a team distribution list and not a personal email",
    )

    # Load Balancer Frontend Configuration
    APPLICATION_HANDLE = forms.CharField(
        required=True,
        label="LB Application Handle",
        initial="Ex. netflex-app",
        widget=forms.TextInput(attrs={'class': 'textinput form-control'}),
        max_length=40,
        strip=True,
        help_text="Use lower case alphanumeric and hyphen (-) characters only",
    )

    SECURITY_ZONE = forms.ChoiceField(
        required=True,
        label="Security Zone",
        choices=[
            ("internal", "Internal (Green)"),
            ("dmz", "DMZ (Blue or Internet or Partner Facing)"),
            ("sensitive", "Sensitive (Black)"),
            ("office", "Office (Red)"),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="",
        
    )
    DATACENTER = forms.ChoiceField(
        required=True,
        label="Site",
        choices=[
            ("as", "Ashburn"),
            ("ch", "Chicago"),
            ("ho", "Hillsboro"),
            ("po", "Potomac"),
            ("wc", "West Chester"),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select a site where your backends are located",
        
    )
    LOADBALANCER_TYPE = forms.ChoiceField(
        required=True,
        label="Load Balancer Type",
        choices=[
            ("https", "Application Load Balancer (HTTPs)"),
            ("http", "Application Load Balancer (HTTP)"),
            ("tcp", "Network Load Balancer (TCP)"),
            ("udp", "Network Load Balancer (UDP)"),
            ("sql", "SQL Load Balancer"),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="See wiki https://etwiki.sys.comcast.net/display/NELB/Load+Balancing+Engineering for help",
        
    )
    VIP_ADDRESS_TYPE = forms.ChoiceField(
        required=True,
        label="VIP Address Type",
        choices=[
            ("ipv4", "IPv4"),
            ("ipv6", "IPv6"),
        ],
        initial="ipv4",
        widget=forms.RadioSelect(attrs={'class': 'form-check-inline'}),
        
    )
    VIP_ADDRESS = forms.GenericIPAddressField(
        label="VIP Address",
        required=False,
        disabled=True,
        widget=forms.TextInput(attrs={'class': 'textinput form-control'}),
        help_text="Allocated VIP Address will be populated here",
        
    )
    VIP_PORT = forms.IntegerField(
        required=True,
        label="VIP Port",
        initial=443,
        widget=forms.TextInput(attrs={'class': 'textinput form-control'}),
        min_value=1,
        max_value=65535,
        help_text="Enter a port number",
    )


    # Advanced Settings

    LOAD_BALANCING_METHODS = forms.ChoiceField(
        required=True,
        choices=[
            ("roundrobin", "Round Robin"),
            ("leastconnections", "Least Connections"),
        ],
        label="Load Balancing Method",
    )
    HEALTH_CHECK_HTTP_URI = forms.CharField(
        #regex=r"^([a-z0-9+.-]+):(?://(?:((?:[a-z0-9-._~!$&'()*+,;=:]|%[0-9A-F]{2})*)@)?((?:[a-z0-9-._~!$&'()*+,;=]|%[0-9A-F]{2})*)(?::(\d*))?(/(?:[a-z0-9-._~!$&'()*+,;=:@/]|%[0-9A-F]{2})*)?|(/?(?:[a-z0-9-._~!$&'()*+,;=:@]|%[0-9A-F]{2})+(?:[a-z0-9-._~!$&'()*+,;=:@/]|%[0-9A-F]{2})*)?)(?:\?((?:[a-z0-9-._~!$&'()*+,;=:/?@]|%[0-9A-F]{2})*))?(?:#((?:[a-z0-9-._~!$&'()*+,;=:/?@]|%[0-9A-F]{2})*))?$",
        #regex=r"^$",
        label="HTTP Health Check URI",
        initial="/health",
        help_text="Enter a URI path to check",
    )
    HEALTH_CHECK_HTTP_EXPECTED_RESPONSE = forms.CharField(
        label="HTTP Expected Response",
        initial="200 OK",
        help_text="Enter the expected response content for health check",
    )
    HEALTH_CHECK_HTTP_HOST_HEADER = forms.CharField(
        label="HTTP Host Header",
        initial="www.example.com",
        help_text="Enter a host header",
    )
    
    HEALTH_CHECK_PORT = forms.IntegerField(
        label="Health Check Port",
        initial=443,
        help_text="Enter a port number if different from Backend Port",
        min_value=1,
        max_value=65535,
    )


class BackendInfoForm(forms.Form):
    ip_address = forms.GenericIPAddressField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    port = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=1,
        max_value=65535
    )
    site = forms.ChoiceField(
        choices=[
            ("as", "Ashburn"),
            ("ch", "Chicago"),
            ("ho", "Hillsboro"),
            ("po", "Potomac"),
            ("wc", "West Chester"),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='Ashburn'
    )
    fqdn = forms.CharField(
        disabled=True,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    admin_state = forms.ChoiceField(
        choices=[('enabled', 'Enabled'), ('disabled', 'Disabled')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='enabled'
    )

BackendInfoFormSet = formset_factory(BackendInfoForm, extra=1, can_delete=True)


class SlbDisplayForm(forms.Form):
    pass