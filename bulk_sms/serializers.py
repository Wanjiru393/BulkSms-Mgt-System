from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class UserProfileRegistrationSerializer(serializers.ModelSerializer):
    staff_number = serializers.CharField(source='userprofile.staff_number')
    full_name = serializers.CharField(source='userprofile.full_name')
    department = serializers.CharField(source='userprofile.department')
    station = serializers.CharField(source='userprofile.station')
    email = serializers.EmailField()
    role = serializers.ChoiceField(source='userprofile.role', choices=UserProfile.ROLE_CHOICES)
    username = serializers.CharField() 

    class Meta:
        model = User
        fields = ('username', 'staff_number', 'full_name', 'password', 'department', 'station', 'email', 'role')

    def create(self, validated_data):
        profile_data = validated_data.pop('userprofile')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user, **profile_data)
        return user
    
class SMSTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSTemplate
        fields = ['id', 'content', 'issue_type']


class SMSSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.userprofile.full_name')
    issue_type = serializers.SlugRelatedField(queryset=SMSTemplate.objects.all(), slug_field='issue_type')
    customer = serializers.SlugRelatedField(queryset=Customer.objects.all(), slug_field='name')
    submission_date = serializers.DateTimeField(read_only=True)
    message_content = serializers.SerializerMethodField()
    approved_by = serializers.ReadOnlyField(source='approved_by.userprofile.full_name')

    class Meta:
        model = SMS
        fields = ['submission_date', 'approval_status', 'issue_type', 'customer', 'created_by', 'message_content', 'batch_number', 'approved_by']

    def create(self, validated_data):
        issue_type = validated_data.pop('issue_type', None)
        if not issue_type:
            raise serializers.ValidationError({"issue_type": "This field is required."})
        customer = validated_data.pop('customer', None)
        if not customer:
            raise serializers.ValidationError({"customer": "This field is required."})
        template = SMSTemplate.objects.get(issue_type=issue_type.issue_type)
        customer = Customer.objects.get(name=customer.name)
        message_content = serializers.SerializerMethodField()
        batch_number = datetime.now().strftime("%Y%m%d") + str(SMS.objects.count() + 1)
        sms = SMS.objects.create(batch_number=batch_number, message_content=message_content, issue_type=template, customer=customer, **validated_data)
        return sms

    def get_message_content(self, obj):
        template = obj.issue_type
        customer = obj.customer
        return self.format_message_content(template, customer)
    
    def update_message_content(self, instance):
        template = instance.issue_type
        customer = instance.customer
        instance.message_content = self.format_message_content(template, customer)
        instance.save()

    def format_message_content(self, template, customer):
        message_content = template.content
        message_content = message_content.replace("{customer_name}", customer.name)
        message_content = message_content.replace("{phone_number}", customer.contact)
        message_content = message_content.replace("{account_number}", customer.account_number)
        return message_content
    
    def to_representation(self, instance):
        self.update_message_content(instance)
        return super().to_representation(instance)