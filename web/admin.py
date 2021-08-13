from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import *


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser

        fields = ('email', )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format

        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(label= ("Password"),
        help_text= ('<a href="../password/">Change Password</a>.'))

    class Meta:
        model = CustomUser
        fields = ('email', 'password','first_name','last_name', 'is_active','is_staff')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class CustomAdmin(UserAdmin):

    list_display = ('email', 'first_name','last_name','is_active','last_login','date_joined',)
    list_filter = ('is_staff', 'is_active',)
    search_fields = (  'email','first_name','last_name')
    ordering = ( 'email',)





    fieldsets = (
        (None, {'fields': ('email', 'password')}),

        (_('Permissions'), {'fields': ('is_active', 'is_staff', )}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),

    )

    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm


admin.site.register(CustomUser, CustomAdmin)

class ReadingAdmin(admin.ModelAdmin):
    list_display = ('rdg_no','timestamp','gadget','temp', 'rh', 'pm_01', 'pm_10','pm_25')
    list_filter = ('timestamp','gadget',)

admin.site.register(Reading, ReadingAdmin)

