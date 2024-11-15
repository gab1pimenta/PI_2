from django.db import models

#classe para criar a tabela no MySQL
class Funcionario(models.Model):
    nome = models.CharField(max_length=255)
    usuario = models.CharField(max_length=150, unique=True)
    senha = models.CharField(max_length=128)  
    funcao = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
    
class PDF(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name="pdfs")
    link = models.URLField()
    
    def __str__(self):
        return f"PDF de {self.funcionario.nome}"
