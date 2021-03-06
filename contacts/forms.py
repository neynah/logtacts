from django import forms
from django.core.exceptions import ValidationError
from haystack.forms import ModelSearchForm

from contacts.models import Contact, LogEntry, Tag

class ContactForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        book = kwargs.pop('book')
        super(ContactForm, self).__init__(*args, **kwargs)
        choices = Tag.objects.filter(book=book).values_list('id', 'tag')
        self.fields['tags'].choices = choices

    class Meta:
        model = Contact
        exclude = ['created', 'changed', 'book', 'last_contact']
        widgets = {
            'tags': forms.CheckboxSelectMultiple(),
            'notes': forms.Textarea(attrs={'rows':3}),
            'address': forms.Textarea(attrs={'rows':3}),
        }


class LogEntryForm(forms.ModelForm):
    USER_SELECTABLE_CHOICES = (
        ('twitter', 'Twitter'),
        ('tumblr', 'Tumblr'),
        ('facebook', 'Facebook'),
        ('email', 'Email'),
        ('in person', 'In Person'),
        ('website', 'Website'),
        ('other', 'Other'),
    )

    kind = forms.ChoiceField(choices=USER_SELECTABLE_CHOICES)

    class Meta:
        model = LogEntry
        fields = ['kind','link','notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows':1}),
        }
 

class TagForm(forms.ModelForm):

    class Meta:
        model = Tag
        fields = ['tag', 'color']

    def clean(self):

        if self.cleaned_data.get('color') and len(self.cleaned_data.get('color')) > 7:
            raise ValidationError("Hex colors must be six digits or less!")

        if self.cleaned_data.get('color') and not self.cleaned_data.get('color').startswith('#'):
            raise ValidationError("Hex must start with #!")

        return self.cleaned_data


class ContactSearchForm(ModelSearchForm):

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        sqs = self.searchqueryset.auto_query(self.cleaned_data['q'])

        if self.load_all:
            sqs = sqs.load_all()

        return sqs


class MultiContactForm(forms.Form):

    def __init__(self, *args, **kwargs):
        contact_ids = kwargs.pop('contact_ids')
        super(MultiContactForm, self).__init__(*args, **kwargs)
        for contact_id in contact_ids:
            self.fields['contact_%s' % (contact_id,)] = forms.BooleanField(
                required=False
            )
