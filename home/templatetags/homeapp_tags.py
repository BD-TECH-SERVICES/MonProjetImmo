from home.models import Tag,BlogCategory
from django.template import Library

register = Library()

@register.inclusion_tag("components/main_categories.html",takes_context=True)
def category_list(context):
    categories = BlogCategory.objects.all()
    return {
        "request" : context["request"],
        "categories" : categories

    }

@register.inclusion_tag("components/main_tags.html",takes_context=True)
def tag_list(context):
    tags = Tag.objects.all()
    return {
        "request" : context["request"],
        "tags" : tags
        
    }