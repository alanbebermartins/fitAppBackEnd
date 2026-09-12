from rest_framework import serializers
from .models import Training, Exercise

# Criar a rota da API para salvar os dados

# No Django, usamos views + serializers (DRF).

class TrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Training
        fields = '__all__'  # ou lista: ['exercise_id', 'peso_kg', ...]
        read_only_fields = (
            'volume_total_weight',
        )


class ExerciseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ('uuid_exercise_id', 'muscle_group', 'exercise_name')


class MuscleGroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ('muscle_group',)
