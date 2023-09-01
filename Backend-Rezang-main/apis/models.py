from django.db import models

class Question(models.Model):
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text

class Option(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    option_id = models.PositiveIntegerField()

    def __str__(self):
        return self.text

class UserResponse(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, on_delete=models.CASCADE)

    def __str__(self):
        return f"User selected '{self.selected_option}' for '{self.question}'"


class Image(models.Model):
    base64_data = models.TextField()
