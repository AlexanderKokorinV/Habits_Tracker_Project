from celery import shared_task
from django.utils import timezone

@shared_task
def send_course_update_email(course_id, user_email):
    """Пример фоновой ресурсоемкой задачи (например, отправка Email)"""
    print(f"Начало фоновой отправки письма для курса {course_id} на email {user_email}...")
    # Здесь в будущем будет вызов send_mail()
    print("Письмо успешно отправлено в фоновом режиме!")
    return True


@shared_task
def check_inactive_users_periodic():
    """Периодическая задача для Celery-Beat: выполняется по расписанию"""
    print(f"Планировщик Celery-Beat сработал в: {timezone.now()}")
    print("Проверка неактивных пользователей выполнена успешно.")