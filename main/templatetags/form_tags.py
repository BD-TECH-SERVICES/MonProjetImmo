from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    """Add CSS class(es) to a form field widget."""
    existing = field.field.widget.attrs.get('class', '')
    new_classes = (existing + ' ' + css).strip()
    return field.as_widget(attrs={**field.field.widget.attrs, 'class': new_classes})
