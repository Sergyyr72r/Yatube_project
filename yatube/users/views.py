from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CreateForm, UpdateProfile


class SignUp(CreateView):
    form_class = CreateForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


@login_required
def profile_edit(request):
    user = get_object_or_404(User, pk=request.user.pk)
    form = UpdateProfile(instance=user)
    if request.method == 'get':
        return render(request, 'users/profile_edit.html', {'form': form})
    if form.is_valid():
        form.save()
        return redirect('posts:profile', username=request.user)
