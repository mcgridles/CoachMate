from __future__ import unicode_literals

from django.forms import ModelForm, BaseFormSet, BaseModelFormSet, formset_factory, modelformset_factory
from django.forms.widgets import CheckboxSelectMultiple, RadioSelect

from teams.models import *

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

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(TeamForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({
            'placeholder': 'Name*',
            'class': 'form-control'
        })
        self.fields['abbr'].widget.attrs.update({
            'placeholder': 'Abbreviation*',
            'class': 'form-control'
        })
        self.fields['region'].widget.attrs.update({
            'placeholder': 'Region',
            'class': 'form-control'
        })

    def save(self):
        team = super(TeamForm, self).save(commit=False)
        team.user = self.user # associate user
        team.save()
        return team


class SwimmerForm(ModelForm):
    class Meta:
        model = Swimmer
        exclude = ['team', 'age']
        labels = {
            'f_name': 'First Name',
            'l_name': 'Last Name',
            'gender': 'M/F',
            'birth_date': 'Birth Date',
            'bio': 'Bio',
        }

    def __init__(self, *args, **kwargs):
        self.team = kwargs.pop('team', None)
        super(SwimmerForm, self).__init__(*args, **kwargs)
        self.fields['f_name'].widget.attrs.update({
            'placeholder': 'First Name*',
            'class': 'form-control'
        })
        self.fields['l_name'].widget.attrs.update({
            'placeholder': 'Last Name*',
            'class': 'form-control'
        })
        self.fields['gender'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['birth_date'].widget.attrs.update({
            'placeholder': 'Birth Date',
            'class': 'form-control'
        })
        self.fields['bio'].widget.attrs.update({
            'placeholder': 'Bio',
            'class': 'form-control'
        })

    def save(self):
        swimmer = super(SwimmerForm, self).save(commit=False)
        swimmer.team = self.team # associate team
        cleaned_data = super(SwimmerForm, self).clean()
        birth_date = cleaned_data.get('birth_date') # check for DoB
        if birth_date:
            swimmer.set_age() # calculate age
        swimmer.save()
        return swimmer


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
        self.practice = kwargs.pop('practice', None)
        self.team = kwargs.pop('team', None)
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
        self.fields['swimmers'].widget = CheckboxSelectMultiple()
        self.fields['swimmers'].queryset = Swimmer.objects.filter(team=self.team).order_by('l_name')
        self.fields['base'].widget = RadioSelect(choices=BASE_CHOICE)

    def clean(self):
        cleaned_data = super(SetForm, self).clean()
        order = cleaned_data.get('order')
        # check for any sets with the same order number
        if Set.objects.filter(practice_id=self.practice).filter(order=order):
            msg = 'Error: Another set already given order #%d' % order
            self.add_error('order', msg)
        return cleaned_data

    def save(self):
        setInstance = super(SetForm, self).save(commit=False)
        setInstance.practice_id = self.practice # associate practice
        setInstance.save()
        return setInstance


class PracticeForm(ModelForm):
    class Meta:
        model = Practice
        fields = ['weekday']
        labels = {'weekday': 'Select Day'}

    def __init__(self, *args, **kwargs):
        self.team = kwargs.pop('team', None)
        self.week_id = kwargs.pop('week', None)
        super(PracticeForm, self).__init__(*args, **kwargs)
        self.fields['weekday'].widget.attrs.update({'class': 'form-control'})

    def save(self):
        practice = super(PracticeForm, self).save(commit=False)
        practice.team = self.team # associate team
        practice.week_id = self.week_id # associate week
        practice.save()
        return practice


class TrainingForm(ModelForm):
    class Meta:
        model = TrainingModel
        fields = ['team']

    def __init__(self, *args, **kwargs):
        super(TrainingForm, self).__init__(*args, **kwargs)
        self.fields['team'].widget.attrs.update({
            'class': 'form-control'
        })

    def save(self):
        training_model = super(TrainingForm, self).save(commit=False)
        team_models = TrainingModel.objects.filter(team=training_model.team)
        for model in team_models:
            model.delete()
        training_model.save()
        return training_model


class MultiplierForm(ModelForm):
    class Meta:
        model = TrainingMultiplier
        exclude = ['training_model']

    def __init__(self, *args, **kwargs):
        super(MultiplierForm, self).__init__(*args, **kwargs)
        self.fields['focus'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['multiplier'].widget.attrs.update({
            'placeholder': 'Multiplier*',
            'class': 'form-control'
        })


# Formsets

class BaseRepFormset(BaseFormSet):
    def save_formset(self, set_id):
        for form in self.forms:
            if form.cleaned_data:
                instance = form.save(commit=False)
                instance.set_id = set_id
                instance.save()

RepFormSet = formset_factory(RepForm, formset=BaseRepFormset)


class BaseMultiplierFormset(BaseModelFormSet):
    def clean(self):
        super(BaseMultiplierFormset, self).clean()
        used = []
        for form in self.forms:
            cleaned_data = form.clean()
            try:
                focus = cleaned_data['focus']

                if focus in used:
                    msg = 'Error: Each intensity can only be assigned 1 multiplier'
                    form.add_error('focus', msg)
                else:
                    used.append(focus)
            except KeyError:
                return


    def save(self, training_model):
        for form in self.forms:
            if form.cleaned_data:
                instance = form.save(commit=False)
                instance.training_model = training_model
                instance.save()

MultiplierFormSet = modelformset_factory(
    TrainingMultiplier,
    form=MultiplierForm,
    formset=BaseMultiplierFormset,
    fields=('focus', 'multiplier')
)
