from django import forms
from django.utils.translation import gettext_lazy as _
from main.models import Customer

class NewServiceForm(forms.ModelForm):
    complain = forms.CharField()
    remark = forms.CharField(widget=forms.Textarea(attrs={'cols': 33, 'rows': 5}))
    class Meta:
        model = Customer
        fields = "__all__"
        exclude = ['customer_id',]

        widgets = {
            'address': forms.Textarea(attrs={'cols': 33, 'rows': 5}),
        }

        labels = {
            'name':_("Full name"),
        }
        error_messages = {

            'name':{
                'required':_("Enter name"),
            }
        }
    
    