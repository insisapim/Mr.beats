from django import template
from ..forms import ProductForm

register = template.Library()

@register.inclusion_tag('upload_beats.html', takes_context=True)
def render_upload_beats(context):
    return {"productForm": ProductForm()}

@register.inclusion_tag('upload_lyrics.html', takes_context=True)
def render_upload_lyrics(context):
    return {"productForm": ProductForm()}