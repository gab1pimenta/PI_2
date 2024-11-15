from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login
from .models import Funcionario, PDF
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from django.urls import reverse

def home(request):
    return render(request, 'home.html') 


def cadastrar_funcionario(request):
    if request.method == 'POST':
        nome = request.POST['nome']
        usuario = request.POST['usuario']
        senha = make_password(request.POST['senha'])
        funcao = request.POST['funcao'].upper()
        
        # Cria o usuário do Django
        user = User.objects.create(username=usuario, password=senha)

        # Cria o funcionário associado
        Funcionario.objects.create(nome=nome, usuario=user, funcao=funcao)

        # Redireciona para a página de sucesso
        return redirect('cadastrar_funcionario_sucesso')  

    return render(request, 'cadastrar_funcionario.html')

def cadastro_sucesso(request):
    return render(request, 'cadastro_sucesso.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Verifica se o usuário existe
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Faz login no sistema
            login(request, user)  


            # Verifica a função do funcionário
            funcionario = Funcionario.objects.get(usuario=user)
            if funcionario.funcao.upper() == 'GESTOR':
                # Redireciona para a página do gestor
                return redirect('pagina_gestor')
            else:
                # Redireciona para a página do funcionário
                return redirect('pagina_funcionario')
            
            
        else:
            return HttpResponse('Usuário não cadastrado. <a href="/cadastrar_funcionario/">Cadastrar Funcionário</a>')
    # Retorna o template de login
    return render(request, 'login.html')  

# Página para gestores
def pagina_gestor(request):
    return render(request, 'pagina_gestor.html') 

def pagina_gestor(request):
    # Obtém a lista de todos os funcionários menos gestores
    funcionarios = Funcionario.objects.exclude(funcao__iexact='gestor')
    return render(request, 'pagina_gestor.html', {'funcionarios': funcionarios})

#Atribuição do PDF ao funcionário
def atribuir_pdf(request, funcionario_id):
    # Autenticação com o Google Drive
    service = authenticate_google_drive()
    results = service.files().list(pageSize=10, fields="files(id, name)").execute()
    items = results.get('files', [])
    
    if not items:
        return HttpResponse("Nenhum arquivo encontrado no Google Drive.")
    
    funcionario = Funcionario.objects.get(id=funcionario_id)
    
    if request.method == 'POST':
        # Obtém o link do PDF selecionado
        pdf_link = request.POST.get('pdf_id')
        
        if not pdf_link:
            return HttpResponse("Nenhum PDF foi selecionado.")
        
        # Cria um novo objeto PDF com o link e associa ao funcionário
        pdf = PDF.objects.create(funcionario=funcionario, link=pdf_link)
        
        return HttpResponse(f"PDF {pdf_link} atribuído ao funcionário {funcionario.nome}. <br> <a href='{reverse('pagina_gestor')}'>Voltar à página do gestor</a>")
    
    return render(request, 'atribuir_pdf.html', {'funcionario': funcionario, 'arquivos': items})


# Página para funcionários
def pagina_funcionario(request):
    funcionario = Funcionario.objects.get(usuario=request.user)
    
    # Acessa o PDF associado ao funcionário, se houver
    pdf = PDF.objects.filter(funcionario=funcionario).first()  # Obtém o primeiro PDF associado
    
    if pdf:
        service = authenticate_google_drive()
        try:
            arquivo = service.files().get(fileId=pdf.link).execute()  # Usa o link do PDF associado
            return render(request, 'pagina_funcionario.html', {'arquivo': arquivo})
        except Exception as e:
            return HttpResponse(f"Ocorreu um erro ao acessar o arquivo: {str(e)}")
    
    # Se não tiver um PDF atribuído
    return HttpResponse("Nenhum PDF atribuído a você.")



#Escopo de acesso para o Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

#Credenciais OAuth 2.0
def authenticate_google_drive():
    flow = InstalledAppFlow.from_client_secrets_file(
        'C:/Users/Nicolas/Documents/PI2/PI_2/view_docs_surgitec/credentials/client_secret_639458682959-i41veectnlmu3em2r4oq4updri6dbov0.apps.googleusercontent.com.json', SCOPES)
    creds = flow.run_local_server(port=8000)
    
    #Serviço de acesso a API do Google Drive
    service = build('drive', 'v3', credentials=creds)
    return service

#Acesso dos arquivos no Google Drive
service = authenticate_google_drive()
results = service.files().list(pageSize=10, fields="files(id, name)").execute()
items = results.get('files', [])

if not items:
    print('Nenhum arquivo encontrado.')
else:
    print('Arquivos:')
    for item in items:
        print(f'{item["name"]} ({item["id"]})')
