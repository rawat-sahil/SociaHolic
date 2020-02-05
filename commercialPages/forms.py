from django import forms

from .models import Com_Page

class Com_PageModelForm(forms.ModelForm):
	class Meta:
		model = Com_Page
		fields = ['title','content','url']