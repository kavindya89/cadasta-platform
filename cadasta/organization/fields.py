from django import forms
from .widgets import ProjectRoleWidget, PublicPrivateToggle, ContactsWidget


class ProjectRoleField(forms.ChoiceField):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        choices = kwargs.get('choices', ())
        self.widget = ProjectRoleWidget(user=user, choices=choices)


class PublicPrivateField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(widget=PublicPrivateToggle, *args, **kwargs)

    def clean(self, value):
        if value:
            value = 'private'
        else:
            value = 'public'
        return value


class ContactsField(forms.Field):
    widget = ContactsWidget

    def __init__(self, form=None, *args, **kwargs):
        self.formset = forms.formset_factory(form)
        super().__init__(*args, **kwargs)

    def clean(self, value):
        cleaned = super().clean(value)
        if hasattr(cleaned, 'cleaned_data'):
            return [val for val in cleaned.cleaned_data
                    if val and not val.pop('remove', False)]
        else:
            raise forms.ValidationError(cleaned.errors)

    def widget_attrs(self, widget):
        return {'formset': self.formset}
