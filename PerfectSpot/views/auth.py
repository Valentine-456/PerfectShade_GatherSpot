from django.views import View
from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from PerfectSpot.forms.auth import CustomUserCreationForm

class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})
    
    def post(self, request):
        # TODO: Implement login API
        pass

class RegisterView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        # TODO: Implement register API
        pass