
from django.forms import ModelForm,forms,ModelChoiceField, Textarea, HiddenInput, CharField, TextInput, ChoiceField


from .models import GadgetLog


class GadgetLogForm(ModelForm):

    choices =  (
        (GadgetLog.ACTION_NOTE, GadgetLog.ACTION_NOTE),
        (GadgetLog.ACTION_NEW_BATTERIES, GadgetLog.ACTION_NEW_BATTERIES),
        (GadgetLog.ACTION_LOCATED, GadgetLog.ACTION_LOCATED),

    )

    action_type = parent_article = ChoiceField(
        choices=choices,
        required=True,
    )
    action = CharField(required=False, min_length=4)

    class Meta:
        model=GadgetLog
        exclude = ['created','creator']
        widgets = {'gadget': HiddenInput(),
                }

