from django import forms
from teams.models import Team, Swimmer, Rep

TeamForm = forms.form_for_model(Team)
SwimmerForm = forms.form_for_model(Swimmer)
RepForm = forms.form_for_model(Rep)
