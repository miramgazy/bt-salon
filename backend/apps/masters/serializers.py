from rest_framework import serializers
from .models import Master, MasterShift
from apps.accounts.models import User
from apps.services.serializers import ServiceSerializer

class MasterSerializer(serializers.ModelSerializer):
    # Map fields from the related User model
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True)
    phone = serializers.CharField(source='user.phone')
    telegram_id = serializers.IntegerField(source='user.telegram_id', required=False, allow_null=True)
    
    services_detail = ServiceSerializer(source='services', many=True, read_only=True)
    photo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Master
        fields = [
            'id', 'organization', 'user', 'first_name', 'last_name', 'phone', 
            'photo', 'photo_url', 'bio', 'color', 'telegram_id', 
            'is_active', 'services', 'services_detail'
        ]
        read_only_fields = ['user', 'photo_url']

    def get_photo_url(self, obj):
        if not obj.photo: return None
        request = self.context.get('request')
        if request: return request.build_absolute_uri(obj.photo.url)
        return obj.photo.url

    def create(self, validated_data):
        user_data = validated_data.pop('user', {})
        if not user_data:
            raise serializers.ValidationError({"user": "Contact information (name/phone) is required."})
            
        # Get organization from validated_data (passed by perform_create) or context
        organization = validated_data.pop('organization', None)
        if not organization:
            organization = self.context['request'].user.organization
        
        # 1. Get or create User
        user = None
        phone = user_data.get('phone')
        tg_id = user_data.get('telegram_id')

        if phone:
            user = User.objects.filter(organization=organization, phone=phone).first()
        
        if not user and tg_id:
            user = User.objects.filter(organization=organization, telegram_id=tg_id).first()

        if user:
            # Update existing user to be a master
            user.role = User.ROLE_MASTER
            for attr, value in user_data.items():
                if value is not None:
                    setattr(user, attr, value)
            user.save()
        else:
            # Create brand new user
            if not phone:
                 raise serializers.ValidationError({"phone": "Phone number is required for new masters."})
            
            # Clean phone for username (unique slug)
            clean_phone = ''.join(filter(str.isdigit, phone))
            username = f"master_{clean_phone}_{organization.id if organization else 'sys'}"
            
            # Check if username exists (rare collision)
            if User.objects.filter(username=username).exists():
                username = f"{username}_{User.objects.count()}"

            user = User.objects.create(
                username=username,
                organization=organization,
                role=User.ROLE_MASTER,
                **user_data
            )
        
        # 2. Create Master profile
        # Pop services as they must be set after creation
        services_data = validated_data.pop('services', [])
        
        master = Master.objects.create(user=user, organization=organization, **validated_data)
        
        if services_data:
            master.services.set(services_data)
            
        return master

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()
        
        return super().update(instance, validated_data)

class MasterShiftSerializer(serializers.ModelSerializer):
    master_name = serializers.CharField(source='master.user.first_name', read_only=True)
    
    class Meta:
        model = MasterShift
        fields = '__all__'
        read_only_fields = ['organization']
