from django import forms

class SignIn(forms.Form):
    mail = forms.CharField(label="E-mail:", max_length=200, widget=forms.TextInput(attrs={'class':'input'})) 
    name = forms.CharField(label="Nom:", max_length=200, widget=forms.TextInput(attrs={'class':'input'})) 
    surname1 = forms.CharField(label="Primer Cognom:", max_length=200, widget=forms.TextInput(attrs={'class':'input'})) 
    pswrd = forms.CharField(label="Contrasenya", widget=forms.PasswordInput(attrs={'class':'input'})) 
    pswrdconfirm = forms.CharField(label="Confirmar Contrasenya",widget=forms.PasswordInput(attrs={'class':'input'})) 

class filterCat(forms.Form):
    name = forms.CharField(label="Nom:", max_length=200, widget=forms.TextInput(attrs={'class':'input'})) 