
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate
from django.contrib import auth
from .forms import LoginForm
from django.contrib.auth.decorators import login_required
from .forms import ProjectForm
from .forms import VideoForm
from .models import Project
from .models import Video
from django.db.models import Max
from django.contrib.auth.models import User
from django.http import Http404

def checkuser(request, prj):
  if request.user.username == prj.teacher.username:
    return True
  return False

@login_required(redirect_field_name='')
def main_page(request):
  return render(request, 'silsite/main_page.html', {'projects': Project.objects.all(), 'user': request.user})

def login(request):
  '''Страница входа'''
  text = 'Вам нужно авторизироваться перед использованием.'
  form = LoginForm(data=(request.POST or None))
  if request.method == 'POST':
    if form.is_valid():
      username = form.cleaned_data['username']
      password = form.cleaned_data['password']
      user = authenticate(username=username, password=password)
      if user is not None:
        if user.is_active:
          auth.login(request, user)
          return redirect('main_page')
        else:
          form = LoginForm()
          text = 'Извините, но ваш аккаунт неактивен'
      else:
        form = LoginForm()
        text = 'Неверное имя пользователя или пароль'
    else:
      form = LoginForm()
      text = 'Неверное имя пользователя или пароль'
  return render(request, 'silsite/login.html', {'form': form, 'text': text})

@login_required(redirect_field_name='')
def new_project(request):
  n = Project.objects.aggregate(Max('id'))['id__max']
  m = 0 if (n == None) else n + 1
  prj = Project(teacher=request.user, name=f'Проект регестрируется#{m}')
  prj.save()
  return render(request, 'silsite/new_project.html', {'project': prj})

  # '''Новый проект'''
  # text_ = 'New project'
  # form = ProjectForm(request.POST or None)
  # if request.method == 'POST':
  #   if form.is_valid():
  #     prj = Project()
  #     prj.name = form.cleaned_data['name']
  #     if request.FILES.get('short_text') != None and request.FILES.get('text') != None and request.FILES.get('presentation') != None:
  #       prj.short_text = request.FILES['short_text']
  #       prj.text = request.FILES['text']
  #       prj.presentation = request.FILES['presentation']
  #     else:
  #       form = ProjectForm(instance=prj)
  #       text_ = 'Please, upload files'
  #       return render(request, 'silsite/new_project.html', {'form': form, 'text_': text_})
  #     prj.teacher = request.user
  #     prj.save()
  #     return redirect('projects')
  #   else:
  #     form = ProjectForm()
  # return render(request, 'silsite/new_project.html', {'form': form, 'text_': text_})

def project_view(request, id):
  '''Просмотр проекта'''
  try:
    project = Project.objects.filter(id=id)[0]
  except Project.DoesNotExist:
    return render(request, 'silsite/error_404.html')
  if request.method == 'POST':
    for i in request.POST:
      try:
        vid = Video.objects.filter(id=int(i))
        vid.delete()
      except ValueError:
        pass
  return render(request, 'silsite/project_view.html', {
    'project': project,
    'username': request.user.username,
    'short_text_name': project.short_text,
    'text_name': project.text,
    'presentation_name': project.presentation,
    'videos': Video.objects.filter(project=project),
  })

@login_required(redirect_field_name='')
def logout(request):
  '''Выход'''
  if (request.method == 'POST'):
    if request.POST.get('Yes') != None:
      auth.logout(request)
      return redirect('login')
    else:
      return redirect('main_page')
  else:
    return render(request, 'silsite/logout.html', {'username': request.user.username})

def error_404(request, exception):
  return render(request, 'silsite/404.html', status=404)

def error_500(request):
  return render(request, 'silsite/404.html', status=500)

def edit_project(request, id):
  text_ = 'Edit project'
  prj = Project.objects.filter(id=id)[0]
  form = ProjectForm()
  if request.method == 'POST':
    form = ProjectForm(request.POST, instance=prj)
    if form.is_valid():
      prj.name = form.cleaned_data['name']
      prj.students = form.cleaned_data['students']
      if request.FILES.get('short_text') != None and request.FILES.get('text') != None and request.FILES.get('presentation') != None:
        prj.short_text = request.FILES['short_text']
        prj.text = request.FILES['text']
        prj.presentation = request.FILES['presentation']
        print(request.FILES['presentation'])
      else:
        form = ProjectForm(instance=prj)
        text_ = 'Please, upload files'
        return render(request, 'silsite/edit_project.html', {'form': form, 'text_': text_, 'short_text': prj.short_text.name})
      prj.save()
      return redirect('main_page')
    else:
      text_ = 'Please, fill the form correctly!'
  else:
    form = ProjectForm(instance=prj)
  return render(request, 'silsite/edit_project.html', {'form': form, 'text_': text_, 'short_text': prj.short_text.name})

def delete_project(request, id):
  if (request.method == 'POST'):
    if request.POST.get('Yes') != None:
      prj = Project.objects.filter(id=id)
      for video in Video.objects.filter(project__in=prj):
        video.delete()
      prj.delete()
    return redirect('main_page')
  else:
    return render(request, 'silsite/delete.html', {})

def add_video(request, id):
  form = VideoForm(data=(request.POST or None))
  if request.method == 'POST':
    if form.is_valid():
      video_wishes = form.cleaned_data['video_wishes']
      video = form.cleaned_data['video']
      vd = Video(video_wishes=video_wishes, video=video, id=(0 if Video.objects.aggregate(Max('id'))['id__max'] == None else Video.objects.aggregate(Max('id'))['id__max'] + 1), project=Project.objects.filter(id=id)[0])
      vd.save()
      return redirect(f'/projects/project/{id}/')
    else:
      form = VideoForm()
  return render(request, 'silsite/add_video.html', {'form': form})

def user_view(request, name):
  projects = Project.objects.filter(teacher__in=User.objects.filter(username=name))
  return render(request, 'silsite/user_view.html', {
    'User': User.objects.filter(username=name)[0],
    'projects': projects
  })
