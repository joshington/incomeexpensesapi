from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
# Create your views here.
from .serializers  import*
from .models import Expense
from rest_framework import permissions
from .permissions import IsOwner

class ExpenseListAPIView(ListCreateAPIView):
    serializer_class = ExpensesSerializer
    queryset = Expense.objects.all()
    permission_classes = (permissions.IsAuthenticated,IsOwner,)

    def perform_create(self,serializer):
        return serializer.save(owner=self.request.user)

    def get_queryset(self):
        #return super().get_queryset()
        return self.queryset.filter(owner=self.request.user)

class ExpenseDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ExpensesSerializer
    queryset = Expense.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "id"


    # def perform_create(self,serializer):
    #     return serializer.save(owner=self.request.user)

    def get_queryset(self):
        #return super().get_queryset()
        return self.queryset.filter(owner=self.request.user)

