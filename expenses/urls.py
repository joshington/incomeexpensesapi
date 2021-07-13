from django.urls import path
from . import views 


app_name="expenses"
urlpatterns = [
    path('',views.ExpenseListAPIView.as_view(),name="expenses"),
    path('<int:id>',views.ExpenseDetailAPIView, name="expenseDetails")
]
