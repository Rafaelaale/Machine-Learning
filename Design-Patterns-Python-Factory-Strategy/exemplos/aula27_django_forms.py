"""Exemplo da transcricao - Django forms.

Requer Django instalado para ser executado.
Deve ser utilizado dentro de um projeto Django
com configuracoes apropriadas.
"""

from django import forms


class ContatoForm(forms.Form):
    nome = forms.CharField(max_length=100)
    email = forms.EmailField()
    mensagem = forms.CharField(widget=forms.Textarea)

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if not email.endswith("@example.com"):
            raise forms.ValidationError(
                "Email deve ser do domínio example.com"
            )

        return email


# O Django implementa internamente is_valid()
# e full_clean(). Nao sobrescrevemos esses metodos.
# clean_email() e o hook personalizado do exemplo.
