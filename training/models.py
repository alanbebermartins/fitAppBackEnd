# Create your models here.
import uuid
from django.db import models

# Função que salva os dados no banco de dados
class Training(models.Model):
    exercise_id = models.UUIDField()  # ID do exercício
    weight_kg = models.FloatField()        # Peso usado
    first_set_reps = models.IntegerField()      # Repetições da série 1
    second_set_reps = models.IntegerField()      # Repetições da série 2
    third_set_reps = models.IntegerField()      # Repetições da série 3
    fourth_set_reps = models.IntegerField()      # Repetições da série 4
    volume_total_weight = models.FloatField(blank=True, null=True)   # ⚠️ CALCULADO NO BACKEND → NÃO VEM DO FRONT
    training_date = models.DateField() # ⚠️ VEM DO FRONT    # Data do treino

    def save(self, *args, **kwargs):
        # Calcula volume automaticamente
        self.volume_total_weight = self.weight_kg * (self.first_set_reps + self.second_set_reps + self.third_set_reps + self.fourth_set_reps)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Treino {self.exercise_id} em {self.training_date}"

# Cria a tabela de exercicios no banco

class Exercise(models.Model):
    uuid_exercise_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    muscle_group = models.CharField(max_length=100)
    exercise_name = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.exercise_name} ({self.muscle_group})"



