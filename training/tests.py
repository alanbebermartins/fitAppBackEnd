import json
from django.test import TestCase
from rest_framework.test import APIClient
from .models import Exercise


class ExerciseListEndpointTest(TestCase):
    def test_get_list_all_exercises_returns_uuid_and_exercise_name_objects(self):
        exercise_a = Exercise.objects.create(
            muscle_group="Peito",
            exercise_name="Supino",
        )
        exercise_b = Exercise.objects.create(
            muscle_group="Costas",
            exercise_name="Remada",
        )

        client = APIClient()
        response = client.get('/api/get_list_all_exercises/')

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)

        self.assertIsInstance(payload, list)
        self.assertGreaterEqual(len(payload), 2)
        self.assertIn(
            {
                "uuid_exercise_id": str(exercise_a.uuid_exercise_id),
                "muscle_group": exercise_a.muscle_group,
                "exercise_name": exercise_a.exercise_name,
            },
            payload,
        )
        self.assertIn(
            {
                "uuid_exercise_id": str(exercise_b.uuid_exercise_id),
                "muscle_group": exercise_b.muscle_group,
                "exercise_name": exercise_b.exercise_name,
            },
            payload,
        )
        for item in payload:
            self.assertEqual(set(item.keys()), {"uuid_exercise_id", "muscle_group", "exercise_name"})


class MuscleGroupListEndpointTest(TestCase):
    def test_get_list_all_muscle_groups_returns_unique_flat_category_objects(self):
        Exercise.objects.create(muscle_group="Peito", exercise_name="Supino")
        Exercise.objects.create(muscle_group="Peito", exercise_name="Press")
        Exercise.objects.create(muscle_group="Costas", exercise_name="Remada")

        client = APIClient()
        response = client.get('/api/get_list_all_muscle_groups/')

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)

        self.assertIsInstance(payload, list)
        self.assertIn({"muscle_group": "Peito"}, payload)
        self.assertIn({"muscle_group": "Costas"}, payload)
        self.assertEqual(len(payload), len({item["muscle_group"] for item in payload})
        )
