from django import forms
from django.utils.datastructures import MultiValueDict
import json


class MultiSelectWidget(forms.Widget):
    template_name = "widgets/multi_select.html"

    def __init__(self, attrs=None):
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        value = value or []
        if not isinstance(value, list):
            value = [value]

        choices = [
            {"label": str(label), "value": str(val)}
            for val, label in self.choices
            if val
        ]

        context["choices"] = json.dumps(choices)
        context["selected"] = value
        context["selected_json"] = json.dumps(value)
        return context

    def value_from_datadict(self, data, files, name):
        """
        Extracts a list of values from the submitted data.
        """
        if isinstance(data, MultiValueDict):
            return data.getlist(name)
        return data.get(name)
