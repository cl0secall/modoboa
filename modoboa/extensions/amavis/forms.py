# coding: utf-8
from django import forms
from modoboa.lib.formutils import InlineRadioSelect
from modoboa.extensions.amavis.models import Policy, Users


class DomainPolicyForm(forms.ModelForm):
    spam_subject_tag2_act = forms.BooleanField()

    class Meta:
        model = Policy
        fields = ('bypass_virus_checks', 'bypass_spam_checks',
                  'spam_tag2_level', 'spam_subject_tag2',
                  'spam_kill_level', 'bypass_banned_checks')
        widgets = {
            'bypass_virus_checks': InlineRadioSelect(),
            'bypass_spam_checks': InlineRadioSelect(),
            'spam_tag2_level': forms.TextInput(attrs={'class': 'col-md-1 form-control'}),
            'spam_kill_level': forms.TextInput(attrs={'class': 'col-md-1 form-control'}),
            'spam_subject_tag2': forms.TextInput(attrs={'class': 'col-md-2 form-control'}),
            'bypass_banned_checks': InlineRadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        if "instance" in kwargs:
            self.domain = kwargs["instance"]
            try:
                policy = Users.objects.get(email="@%s" % self.domain.name).policy
                kwargs["instance"] = policy
            except (Users.DoesNotExist, Policy.DoesNotExist):
                del kwargs["instance"]
        super(DomainPolicyForm, self).__init__(*args, **kwargs)
        for f in self.fields.keys():
            self.fields[f].required = False

    def save(self, user, commit=True):
        policy = super(DomainPolicyForm, self).save(commit=False)
        for field in ['bypass_spam_checks', 'bypass_virus_checks',
                  'bypass_banned_checks']:
            if getattr(policy, field) == '':
                setattr(policy, field, None)

        if self.cleaned_data['spam_subject_tag2_act']:
            policy.spam_subject_tag2 = None

        if commit:
            policy.save()
            try:
                u = Users.objects.get(fullname=policy.policy_name)
            except Users.DoesNotExist:
                u = Users.objects.get(email="@%s" % self.domain.name)
                u.policy = policy
                policy.save()
        return policy
