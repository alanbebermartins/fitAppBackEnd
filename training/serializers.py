from rest_framework import serializers
from .models import Training

# Criar a rota da API para salvar os dados

# No Django, usamos views + serializers (DRF).

class TrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Training
        fields = '__all__'  # ou lista: ['exercise_id', 'peso_kg', ...]
        read_only_fields = (
            'volume_total_weight',
        )
