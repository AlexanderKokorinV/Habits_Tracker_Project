from rest_framework import serializers

from habits.models import Habit


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для модели привычки"""
    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ["user"]

    def validate(self, data):
        """Валидатор данных привычки"""
        related_habit = data.get("related_habit", self.instance.related_habit if self.instance else None)
        reward = data.get("reward", self.instance.reward if self.instance else None)
        is_pleasant = data.get("is_pleasant", self.instance.is_pleasant if self.instance else False)
        duration = data.get("duration", self.instance.duration if self.instance else 0)
        periodicity = data.get("periodicity", self.instance.periodicity if self.instance else 1)

        # Исключаем одновременный выбор связанной привычки и вознаграждения
        if related_habit and reward:
            raise serializers.ValidationError(
                "Нельзя одновременно заполнить 'Связанную привычку' и 'Вознаграждение'."
                "Можно заполнить только одно из двух полей."
            )

        # Время выполнения не должно быть больше 120 секунд (Правило 2 минут)
        if duration > 120:
            raise serializers.ValidationError(
                "Время выполнения должно быть не больше 120 секунд."
            )

        # В связанные привычки могут попадать только привычки с признаком приятной
        if related_habit and not related_habit.is_pleasant:
            raise serializers.ValidationError(
                "Связанная привычка обязательно должна иметь признак приятной."
            )

        # У приятной привычки не может быть вознаграждения или связанной привычки
        if is_pleasant and (related_habit or reward):
            raise serializers.ValidationError(
                "У приятной привычки не может быть вознаграждения или связанной привычки."
            )

        # Нельзя выполнять привычку реже, чем 1 раз в 7 дней
        if periodicity > 7:
            raise serializers.ValidationError(
                "Периодичность выполнения привычки не может быть реже, чем раз в 7 дней."
            )

        return data
