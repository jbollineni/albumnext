from django import forms
from crispy_forms.helper import FormHelper
from django.utils.safestring import mark_safe
from crispy_forms.layout import Layout, Row, Column, Field, Div, HTML, ButtonHolder, Submit
from crispy_forms.bootstrap import InlineRadios, AccordionGroup, Accordion, PrependedText, AppendedText, StrictButton, FieldWithButtons
from django.forms import formset_factory
from django.utils.safestring import mark_safe


class SlbCreateForm(forms.Form):

    # Admin Information
    DEVHUB_APP_NAME = forms.ChoiceField(
        label="Devhub Application Name",
        choices=[
            ("convoy", "Convoy"),
            ("einstein", "Einstein"),
            ("teamdevops", "Team-DevOps"),
        ],
        help_text="Select your Devhub application name",
    )
    TEAM_DISTRO_LIST = forms.EmailField(
        label="Team Distribution List",
        initial="Ex. team@example.net",
        help_text="Must be a team distribution list and not a personal email",
    )

    # Load Balancer Frontend Configuration
    APPLICATION_HANDLE = forms.CharField(
        max_length=40,
        label="Application Handle",
        initial="Ex. netflex-app",
        #help_text="Use lower case alphanumeric and hyphen (-) characters only",
        strip=True,
    )
    SECURITY_ZONE = forms.ChoiceField(
        choices=[
            ("green", "Green (Internal)"),
            ("blue", "Blue (DMZ / Internet or Partner Facing)"),
            ("black", "Black (Sensitive)"),
            ("red", "Red (Office)"),
        ],
        # widget=forms.RadioSelect,
        label="Security Zone",
    )
    DATACENTER = forms.ChoiceField(
        choices=[
            ("as", "Ashburn"),
            ("ch", "Chicago"),
            ("ho", "Hillsboro"),
            ("po", "Potomac"),
            ("wc", "West Chester"),
        ],
        help_text="Select a site where your backends are located",
        label="Site",
    )
    LOADBALANCER_TYPE = forms.ChoiceField(
        choices=[
            ("https", "Application Load Balancer (HTTPs)"),
            ("http", "Application Load Balancer (HTTP)"),
            ("tcp", "Network Load Balancer (TCP)"),
            ("udp", "Network Load Balancer (UDP)"),
            ("sql", "SQL Load Balancer"),
        ],
        label="Load Balancer Type",
    )
    VIP_ADDRESS_TYPE = forms.ChoiceField(
        choices=[
            ("ipv4", "IPv4"),
            ("ipv6", "IPv6"),
        ],
        widget=forms.RadioSelect,
        label="VIP Address Type",
    )
    VIP_ADDRESS = forms.GenericIPAddressField(
        label="VIP Address",
        disabled=True,
        help_text="Allocated VIP Address will be populated here",
        
    )
    VIP_PORT = forms.IntegerField(
        label="VIP Port",
        initial=443,
        help_text="Enter a port number",
        min_value=1,
        max_value=65535,
        
    )

    BACKEND_PORT = forms.IntegerField(  
        min_value=1,
        max_value=65535,
    )


    # Advanced Settings

    LOAD_BALANCING_METHODS = forms.ChoiceField(
        choices=[
            ("roundrobin", "Round Robin"),
            ("leastconnections", "Least Connections"),
        ],
        label="Load Balancing Method",
    )
    HEALTH_CHECK_HTTP_URI = forms.RegexField(
        regex=r"^([a-z0-9+.-]+):(?://(?:((?:[a-z0-9-._~!$&'()*+,;=:]|%[0-9A-F]{2})*)@)?((?:[a-z0-9-._~!$&'()*+,;=]|%[0-9A-F]{2})*)(?::(\d*))?(/(?:[a-z0-9-._~!$&'()*+,;=:@/]|%[0-9A-F]{2})*)?|(/?(?:[a-z0-9-._~!$&'()*+,;=:@]|%[0-9A-F]{2})+(?:[a-z0-9-._~!$&'()*+,;=:@/]|%[0-9A-F]{2})*)?)(?:\?((?:[a-z0-9-._~!$&'()*+,;=:/?@]|%[0-9A-F]{2})*))?(?:#((?:[a-z0-9-._~!$&'()*+,;=:/?@]|%[0-9A-F]{2})*))?$",
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





    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-lg-4"
        self.helper.field_class = "col-lg-8"

        self.helper.layout = Layout(
            Row(
                HTML("""
                    <div class="h3">
                        SLB VIP Creation
                    </div>
                """),
                HTML("""
                    <div class="alert alert-warning" role="alert">
                        <strong>Note:</strong> Use this form to create an SLB VIP to loadbalance traffic to your backends (application servers) within a site.
                    </div>
                """),
                HTML('<hr style="height:2px;border-width:0;color:gray;background-color:gray">'),
                Column(
                    Accordion(
                        
                        AccordionGroup(
                            "Admin Information",
                            Div(
                                "DEVHUB_APP_NAME",
                                "TEAM_DISTRO_LIST",
                                # css_class="border p-3",
                            ),
                        ),
                        AccordionGroup(
                            "LB Frontend Config",
                            HTML("""
                                <div class="alert alert-info" role="alert">
                                    <strong>Note:</strong> Use the same application handle of an existing VIP if you intend to open a new port.
                                </div>
                            """),
                            Div(
                                "APPLICATION_HANDLE"
                            ),
                            Div(
                                "SECURITY_ZONE"
                                
                            ),
                            Div(
                                Field("DATACENTER", style="color: #333;", id="frontend-datacenter", css_class='frontend-datacenter')
                            ),
                            Div(
                                Field("LOADBALANCER_TYPE", style="color: #333;", id="frontend-loadbalancer-type", css_class='frontend-loadbalancer-type')
                            ),
                            Div(
                                InlineRadios("VIP_ADDRESS_TYPE")
                            ),
                            Div(
                                FieldWithButtons("VIP_ADDRESS", StrictButton("Retrieve", css_class="btn-info"), input_size="input-group-sm")
                            ),
                            Div(
                                Field("VIP_PORT", style="color: #333;", id="frontend-port", css_class='frontend-port'),
                                # css_class="border p-3",
                            ),
                        ),
                        AccordionGroup(
                            "Advanced Settings",
                            Div(
                                "LOAD_BALANCING_METHODS",
                                # css_class="border p-3",
                            ),
                            Div(
                                "HEALTH_CHECK_HTTP_URI",
                                # css_class="border p-3",
                            ),
                            Div(
                                "HEALTH_CHECK_HTTP_EXPECTED_RESPONSE",
                                # css_class="border p-3",
                            ),
                            Div(
                                "HEALTH_CHECK_HTTP_HOST_HEADER",
                                # css_class="border p-3",
                            ),
                            Div(
                                "HEALTH_CHECK_PORT",
                                # css_class="border p-3",
                            ),
                        css_class="border p-2",
                        )
                    ),
                    css_class="col-md-4",
                ),
                Column(
                    Div(
                        Accordion(
                            AccordionGroup('Backend Information',
                                HTML("""
                                <table class="table" id="backend-table">
                                <colgroup>
                                    <col style="width:20%">
                                    <col style="width:10%">
                                    <col style="width:15%">
                                    <col style="width:35%">
                                    <col style="width:15%">
                                    <col style="width:5%">
                                </colgroup>  
                                    <thead>
                                        <tr>
                                            <th>IP Address</th>
                                            <th>Port</th>
                                            <th>Site</th>
                                            <th>FQDN</th>
                                            <th>Admin State</th>
                                            <th></th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        
                                    </tbody>
                                </table>
                                <button type="button" class="btn btn-primary" id="add-row">Add Row</button>
                                """)
                            ),
                        ),
                        css_class='col-md-12'
                    ),
                    HTML("<br><br>"),
                    ButtonHolder(
                        Submit('submit', 'Save to DB', css_class='btn-info'),
                        Submit('commit', 'Commit to Loadbalancer', css_class='btn-warning')
                    )
                        ),
                        # Empty column for future use
                    ),


           HTML('<hr style="height:2px;border-width:0;color:gray;background-color:gray">'),
            Row(
                Column(
                    Accordion(
                        AccordionGroup(
                            "Event Stream",
                            HTML("<h6> Event Stream </h6>"),
                            css_class="col-md-2"
                        ),
                    
                    ),
                    css_class="col-md-5",
                ),
                Column(
                    Accordion(
                        AccordionGroup(
                            "Traffic flow",
                            HTML("<h6> Network Diagram </h6>"),
                            css_class="col-md-2"
                        ),
                    
                    ),
                    css_class="col-md-7",
                )
            )
        )


class SlbDisplayForm(forms.Form):
    pass