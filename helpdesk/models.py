from django.db import models
from django.contrib.auth.models import User


CATEGORY_CHOICES = [
    ('IND', 'Individual'),
    ('RES', 'Residential'),
    ('EDU', 'Education'),
    ('HTH', 'Health'),
    ('FIS', 'Financial Institution'),
    ('REG', 'Religious'),
    ('BUS', 'Business/Manufacturing'),
    ('GOV', 'Government Agencies'),
    ('SME', 'Business/SME'),

 ]


PRIORITY_CHOICES = [
    ('High', 'High'),
    ('Medium', 'Medium'),
    ('Low', 'Low'),

 ]


REQUEST_CHOICES = [
    ('Password reset', 'Password reset'),
    ('Account Update', 'Account Update'),
    ('User update', 'User update'),
    ('Other', 'Other'),

 ]


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=3, choices=CATEGORY_CHOICES)
    request_type = models.CharField(max_length=50, choices=REQUEST_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


 #category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)