from django.urls import path
from . import views 


app_name = 'income'

urlpatterns = [
    path('',views.IncomeListAPIView.as_view(),name="incomes"),
    path('<int:id>',views.IncomeDetailAPIView, name="income")
]
