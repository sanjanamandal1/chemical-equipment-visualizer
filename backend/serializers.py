from rest_framework import serializers
from .models import Dataset

class DatasetSerializer(serializers.ModelSerializer):
    """Serializer for Dataset model with all fields"""
    
    class Meta:
        model = Dataset
        fields = [
            'id',
            'name',
            'uploaded_at',
            'file',
            'total_count',
            'avg_flowrate',
            'avg_pressure',
            'avg_temperature'
        ]
        read_only_fields = ['uploaded_at']
    
    def to_representation(self, instance):
        """Customize the representation"""
        representation = super().to_representation(instance)
        # Format the uploaded_at date
        if instance.uploaded_at:
            representation['uploaded_at'] = instance.uploaded_at.isoformat()
        return representation