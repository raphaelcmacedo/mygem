from django import template

register = template.Library()

@register.filter(name='addcss')
def addcss(value, arg):
    current_css = value.field.widget.attrs.get('class', None)
    if current_css:
        css_classes = current_css.split(' ')
        if css_classes and arg not in css_classes:
            css_classes = '%s %s' % (css_classes, arg)
    else:
        css_classes = arg
    return value.as_widget(attrs={'class': css_classes})