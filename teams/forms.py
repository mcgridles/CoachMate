from django import forms
from django.forms import ModelForm, BaseFormSet
from django.forms import formset_factory, inlineformset_factory

from teams.models import Team, Swimmer, Rep, Set, Practice

# Model forms

class TeamForm(ModelForm):
    class Meta:
        model = Team
        exclude = ['user']
        labels = {
            'name': 'Team Name',
            'abbr': 'Team Abbreviation',
            'region': 'Team Region',
        }

class SwimmerForm(ModelForm):
    class Meta:
        model = Swimmer
        exclude = ['team']
        labels = {
            'f_name': 'First Name',
            'l_name': 'Last Name',
            'gender': 'M/F',
            'age': 'Age',
            'bio': 'Bio',
        }

class RepForm(ModelForm):
    class Meta:
        model = Rep
        exclude = ['set_id']

    def __init__(self, *args, **kwargs):
        super(RepForm, self).__init__(*args, **kwargs)
        self.fields['num'].widget.attrs.update({
                'placeholder': 'Number',
                'class': 'form-control'
            })
        self.fields['distance'].widget.attrs.update({
                'placeholder': 'Distance',
                'class': 'form-control'
            })
        self.fields['stroke'].widget.attrs.update({
                'class': 'form-control'
            })
        self.fields['rest'].widget.attrs.update({
                'placeholder': 'Rest (optional)',
                'class': 'form-control'
            })
        self.fields['comments'].widget.attrs.update({
                'placeholder': 'Addtional Info (optional)',
                'class': 'form-control'
            })

class SetForm(ModelForm):
    class Meta:
        model = Set
        exclude = ['practice_id']

    def __init__(self, *args, **kwargs):
        super(SetForm, self).__init__(*args, **kwargs)
        self.fields['repeats'].widget.attrs.update({
                'placeholder': 'Repeats (optional)',
                'class': 'form-control'
            })
        self.fields['focus'].widget.attrs.update({
                'class': 'form-control'
            })
        self.fields['order'].widget.attrs.update({
                'placeholder': 'Order Number',
                'class': 'form-control'
            })

class PracticeForm(ModelForm):
    class Meta:
        model = Practice
        fields = ['weekday']
        labels = {'weekday': 'Select Day'}

    def __init__(self, *args, **kwargs):
        super(PracticeForm, self).__init__(*args, **kwargs)
        self.fields['weekday'].widget.attrs.update({'class': 'form-control'})

class BaseRepFormset(BaseFormSet):
    def save_formset(self, set_id):
        for form in self.forms:
            if form.cleaned_data:
                instance = form.save(commit=False)
                instance.set_id = set_id
                instance.save()

RepFormSet = formset_factory(RepForm, formset=BaseRepFormset)
RepInlineFormSet = inlineformset_factory(Set, Rep, form=RepForm, extra=1)
