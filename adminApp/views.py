from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render


# Create your views here.
def logout_view(request):
    logout(request)
    return redirect('adminApp:login')


def register_view(request):
    if request.method != 'POST':
        form = UserCreationForm()
    else:
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()
            auth_user = authenticate(username=new_user.username,
                                     password=request.POST['password1'])
            login(request, auth_user)
            return redirect('userApp:index')
    context = {'form': form}
    return render(request, 'adminApp/register.html', context)
