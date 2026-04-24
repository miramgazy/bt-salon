from rest_framework import serializers
from .models import Expense, ExpenseCategory

class OrganizationDefault:
    requires_context = True
    def __call__(self, serializer_field):
        return serializer_field.context['request'].user.organization

class ExpenseCategorySerializer(serializers.ModelSerializer):
    expenses_count = serializers.IntegerField(read_only=True)
    organization = serializers.HiddenField(default=OrganizationDefault())

    class Meta:
        model = ExpenseCategory
        fields = ['id', 'name', 'expenses_count', 'organization']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ExpenseCategory.objects.all(),
                fields=['name', 'organization'],
                message="Статья с таким названием уже существует."
            )
        ]

class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Expense
        fields = [
            'id', 'date', 'name', 'category', 'category_name', 
            'amount', 'comment', 'created_at', 'updated_at'
        ]

class ExpenseWriteSerializer(serializers.ModelSerializer):
    organization = serializers.HiddenField(default=OrganizationDefault())
    
    class Meta:
        model = Expense
        fields = ['id', 'date', 'name', 'category', 'amount', 'comment', 'organization']
