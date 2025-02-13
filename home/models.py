from django.db import models
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.images.models import Image  
from wagtail.snippets.models import register_snippet
from taggit.models import Tag as TaggitTag
from modelcluster.fields import ParentalKey
from wagtail.snippets.widgets import AdminSnippetChooser  
from taggit.models import TaggedItemBase
from modelcluster.tags import ClusterTaggableManager


# ✅ Correction : Ajout explicite d'un BigAutoField pour éviter le warning
class BaseModel(models.Model):
    id = models.BigAutoField(primary_key=True)

    class Meta:
        abstract = True


@register_snippet
class BlogCategory(BaseModel):
    """Modèle représentant une catégorie de blog dans Wagtail."""

    name = models.CharField(max_length=250, blank=True, verbose_name="Nom")
    slug = models.SlugField(max_length=80, unique=True, verbose_name="Slug")

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"


class PostPageBlogCategory(BaseModel):
    """Relation entre une page d'article et une catégorie de blog."""
    
    page = ParentalKey("home.PostPage", on_delete=models.CASCADE, related_name="categories")
    blog_category = models.ForeignKey("home.BlogCategory", on_delete=models.CASCADE, related_name="post_pages")

    panels = [
        FieldPanel("blog_category", widget=AdminSnippetChooser(BlogCategory)),  
    ]

    class Meta:
        unique_together = ("page", "blog_category")


# ✅ Correction : Remplacement de related_name="+" par related_name="postpagetags"
class PostPageTags(TaggedItemBase):
    content_object = ParentalKey("home.PostPage", related_name="postpagetags")


@register_snippet
class Tag(TaggitTag):
    class Meta:
        proxy = True


class BlogPage(Page):
    """Page contenant plusieurs articles de blog"""

    description = models.CharField(max_length=250, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("description"),
    ]


class PostPage(Page):
    """Modèle représentant un article de blog."""

    template = "home/post_page.html" 

    header_image = models.ForeignKey(
        Image, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="post_header_images"
    )

    tags = ClusterTaggableManager(through="home.PostPageTags", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("header_image"),  
        FieldPanel("tags"),
        InlinePanel("categories", label="Category"),  # ✅ Correction du nom
    ]

