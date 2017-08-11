from __future__ import unicode_literals

import django.forms as forms

from teams.models import *

# Model forms

class TeamForm(forms.ModelForm):
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


class SwimmerForm(forms.ModelForm):
    class Meta:
        model = Swimmer
        exclude = ['team', 'age']
        labels = {
            'f_name': 'First Name',
            'l_name': 'Last Name',
            'gender': 'M/F',
            'birth_date': 'Birth Date',
            'bio': 'Bio',
            'picture': 'Picture',
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
        self.fields['picture'].widget.attrs.update({
            'class': 'form-control'
        })

    def save(self):
        swimmer = super(SwimmerForm, self).save(commit=False)
        swimmer.team = self.team # associate team
        swimmer.set_age() # calculate age
        return swimmer


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ['swimmer']
        labels = {
            'event': 'Event',
            'time': 'Time',
            'date': 'Date',
        }

    def __init__(self, *args, **kwargs):
        self.swimmer = kwargs.pop('swimmer', None)
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['event'].widget.attrs.update({
            'placeholder': 'Event',
            'class': 'form-control'
        })
        self.fields['time'].widget.attrs.update({
            'placeholder': 'Time',
            'class': 'form-control'
        })
        self.fields['date'].widget.attrs.update({
            'placeholder': 'Date',
            'class': 'form-control'
        })

    def save(self):
        event = super(EventForm, self).save(commit=False)
        event.swimmer = self.swimmer # associate swimmer
        event.save()
        return event

class RepForm(forms.ModelForm):
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


class SetForm(forms.ModelForm):
    class Meta:
        model = Set
        exclude = ['practice_id']

    def __init__(self, *args, **kwargs):
        self.practice = kwargs.pop('practice', None)
        self.team = kwargs.pop('team', None)
        super(SetForm, self).__init__(*args, **kwargs)
        self.fields['group'].widget = forms.widgets.RadioSelect(choices=GROUP_CHOICE)
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
        self.fields['swimmers'].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields['swimmers'].queryset = Swimmer.objects.filter(team=self.team)
        self.fields['pace'].widget = forms.widgets.RadioSelect(choices=PACE_CHOICE)

    def clean(self):
        cleaned_data = super(SetForm, self).clean()
        order = cleaned_data.get('order')
        # check for any sets with the same order number
        _set = Set.objects.filter(practice_id=self.practice).filter(order=order)
        if _set.exists():
            msg = 'ERROR: Another set already given order #%d.' % order
            self.add_error('order', msg)

        group = cleaned_data.get('group')
        swimmers = cleaned_data.get('swimmers')
        # swimmers should be chosen or "Team" should be selected
        if group == 'ind' and not swimmers:
            msg = 'ERROR: Select \'Team\' or choose swimmers.'
            self.add_error('group', msg)
        return cleaned_data

    def save(self):
        setInstance = super(SetForm, self).save(commit=False)
        if self.practice:
            setInstance.practice_id = self.practice # associate practice
            setInstance.save()
        self.save_m2m()

        swimmers = Swimmer.objects.filter(team=self.team)
        if setInstance.group == 'team' and swimmers.exists():
            for swimmer in swimmers.iterator():
                setInstance.swimmers.add(swimmer.id)
        setInstance.save()
        return setInstance


class PracticeForm(forms.ModelForm):
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


class TrainingForm(forms.ModelForm):
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


class MultiplierForm(forms.ModelForm):
    class Meta:
        model = TrainingMultiplier
        exclude = ['training_model']

    def __init__(self, *args, **kwargs):
        super(MultiplierForm, self).__init__(*args, **kwargs)
        self.fields['focus'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['multiplier'].widget.attrs.update({
            'placeholder': 'Percentage*',
            'class': 'form-control'
        })


# Formsets

class BaseRepFormset(forms.BaseModelFormSet):
    def save_formset(self, set_id):
        for form in self.forms:
            if form.cleaned_data:
                instance = form.save(commit=False)
                instance.set_id = set_id
                instance.save()

RepFormSet = forms.modelformset_factory(
    Rep,
    form=RepForm,
    formset=BaseRepFormset,
    fields=('num', 'distance', 'stroke', 'rest', 'comments')
)


class BaseMultiplierFormset(forms.BaseModelFormSet):
    def clean(self):
        super(BaseMultiplierFormset, self).clean()
        used = []
        for form in self.forms:
            cleaned_data = form.clean()
            try:
                focus = cleaned_data['focus']

                if focus in used:
                    msg = 'ERROR: Each intensity can only be assigned 1 multiplier'
                    form.add_error('focus', msg)
                else:
                    used.append(focus)

                mult = cleaned_data['multiplier']
                try:
                    if mult.endswith('%'):
                        float(mult[:-1])
                    else:
                        float(mult)
                except ValueError:
                    msg = '%s is not a valid percent' % mult
                    self.add_error('multiplier', msg)
            except KeyError:
                return


    def save(self, training_model):
        for form in self.forms:
            if form.cleaned_data:
                instance = form.save(commit=False)
                instance.training_model = training_model

                try:
                    mult = form.cleaned_data['multiplier']
                    if mult.endswith('%'):
                        instance.multiplier = float(mult[:-1])/100
                    else:
                        instance.multiplier = float(mult)
                except KeyError:
                    return

                instance.save()

MultiplierFormSet = forms.modelformset_factory(
    TrainingMultiplier,
    form=MultiplierForm,
    formset=BaseMultiplierFormset,
    fields=('focus', 'multiplier')
)

class UploadZipForm(forms.Form):
    zip_file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super(UploadZipForm, self).__init__(*args, **kwargs)
        self.fields['zip_file'].widget.attrs.update({
            'class': 'form-control'
        })

    def clean(self):
        cleaned_data = super(UploadZipForm, self).clean()
        file = self.cleaned_data.get('zip_file')
        if file and file.name[-4:].lower() != '.zip':
            msg = 'ERROR: File must be in ZIP format'
            self.add_error('zip_file', msg)
        return cleaned_data
