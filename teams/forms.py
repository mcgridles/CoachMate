from __future__ import unicode_literals

from django.forms import ModelForm, BaseFormSet, ValidationError
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
            'birth_date': 'DOB',
            'bio': 'Bio',
        }

class RepForm(ModelForm):
    class Meta:
        model = Rep
        exclude = ['set_id']

    def __init__(self, *args, **kwargs):
        super(RepForm, self).__init__(*args, **kwargs)
        self.fields['num'].widget.attrs.update({
                'placeholder': 'Number*',
                'class': 'form-control'
            })
        self.fields['distance'].widget.attrs.update({
                'placeholder': 'Distance*',
                'class': 'form-control'
            })
        self.fields['stroke'].widget.attrs.update({
                'class': 'form-control'
            })
        self.fields['rest'].widget.attrs.update({
                'placeholder': 'Rest',
                'class': 'form-control'
            })
        self.fields['comments'].widget.attrs.update({
                'placeholder': 'Comments',
                'class': 'form-control'
            })

class SetForm(ModelForm):
    class Meta:
        model = Set
        exclude = ['practice_id']

    def __init__(self, *args, **kwargs):
        self.p_id = kwargs.pop('p_id', None)
        super(SetForm, self).__init__(*args, **kwargs)
        self.fields['focus'].widget.attrs.update({
                'class': 'form-control'
            })
        self.fields['repeats'].widget.attrs.update({
                'placeholder': 'Repeats',
                'class': 'form-control'
            })
        self.fields['order'].widget.attrs.update({
                'placeholder': 'Set Order*',
                'class': 'form-control'
            })

    def clean(self):
        cleaned_data = super(SetForm, self).clean()
        order = cleaned_data.get('order')
        if Set.objects.filter(practice_id=self.p_id).filter(order=order):
            msg = 'Error: Another set already given order #%d' % order
            self.add_error('order', msg)

        return cleaned_data

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
                instance.set_id = Set.objects.get(id=set_id)
                instance.save()

RepFormSet = formset_factory(RepForm, formset=BaseRepFormset)
RepInlineFormSet = inlineformset_factory(Set, Rep, form=RepForm, extra=1)
