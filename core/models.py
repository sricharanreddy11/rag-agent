from django.db import models


class LLMConfiguration(models.Model):
    config_name = models.CharField(max_length=255, null=True, blank=True)
    llm_provider = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=255, null=True, blank=True)
    llm_info = models.ForeignKey(
        'LLMInfo',on_delete=models.SET_NULL, null=True, blank=True, related_name='llm_configurations'
    )
    config_type = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    system_behaviour = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    response_count = models.IntegerField(default=1)
    config_data = models.JSONField(null=True, blank=True)
    meta_data = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'llm_config'


class LLMRequestLog(models.Model):
    user_id = models.CharField(max_length=255, null=True, blank=True)
    request_model = models.CharField(max_length=255, null=True, blank=True)
    config_name = models.CharField(max_length=255, null=True, blank=True)
    request_type = models.CharField(max_length=255, null=True, blank=True)
    request_data = models.JSONField(default=dict)
    response_data = models.JSONField(default=dict)
    input_tokens = models.IntegerField(default=0, null=True, blank=True)
    output_tokens = models.IntegerField(default=0, null=True, blank=True)
    meta_data = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    response_cost = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'llm_request_log'

class LLMInfo(models.Model):
    model_name = models.CharField(max_length=255, unique=True)
    provider = models.CharField(max_length=255, choices=[
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic')])
    pricing = models.JSONField(default=dict)
    description = models.TextField(null=True, blank=True)
    capabilities = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    meta_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'llm_info'