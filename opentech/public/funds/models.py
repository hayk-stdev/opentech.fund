from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core import validators
from django.db import models
from django.utils.deconstruct import deconstructible

from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from wagtail.core.fields import StreamField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from opentech.public.utils.models import (
    BasePage,
    RelatedPage,
)

from .blocks import FundBlock, LabBlock


class BaseApplicationRelatedPage(RelatedPage):
    source_page = ParentalKey('BaseApplicationPage', related_name='related_pages')


class BaseApplicationPage(BasePage):
    subpage_types = []
    parent_page_types = []

    application_type_model = ''

    introduction = models.TextField(blank=True)
    application_type = models.ForeignKey(
        'wagtailcore.Page',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='application_public',
    )
    body = StreamField(FundBlock())

    search_fields = BasePage.search_fields + [
        index.SearchField('introduction'),
        index.SearchField('body')
    ]

    content_panels = BasePage.content_panels + [
        FieldPanel('introduction'),
        StreamFieldPanel('body'),
        InlinePanel('related_pages', label="Related pages"),
    ]

    def get_template(self, request, *args, **kwargs):
        # Make sure all children use the shared template
        return 'public_funds/fund_page.html'

    can_open = True

    @property
    def is_open(self):
        return self.application_type and bool(self.application_type.specific.open_round)

    @property
    def deadline(self):
        return self.application_type and self.application_type.specific.next_deadline()


class FundPage(BaseApplicationPage):
    parent_page_types = ['FundIndex']
    content_panels = BaseApplicationPage.content_panels[:]
    content_panels.insert(-2, PageChooserPanel('application_type', 'funds.FundType'))


class RFPPage(BaseApplicationPage):
    parent_page_types = ['LabPage']
    content_panels = BaseApplicationPage.content_panels[:]
    content_panels.insert(-2, PageChooserPanel('application_type', 'funds.RequestForPartners'))


class FundIndex(BasePage):
    subpage_types = ['FundPage']
    parent_page_types = ['home.HomePage']

    introduction = models.TextField(blank=True)

    content_panels = BasePage.content_panels + [
        FieldPanel('introduction')
    ]

    def get_context(self, request, *args, **kwargs):
        funds = FundPage.objects.live().public().descendant_of(self)

        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(funds, settings.DEFAULT_PER_PAGE)
        try:
            funds = paginator.page(page)
        except PageNotAnInteger:
            funds = paginator.page(1)
        except EmptyPage:
            funds = paginator.page(paginator.num_pages)

        context = super().get_context(request, *args, **kwargs)
        context.update(subpages=funds)
        return context


class LabPageRelatedPage(RelatedPage):
    source_page = ParentalKey('LabPage', related_name='related_pages')


@deconstructible
class MailToAndURLValidator:
    email_validator = validators.EmailValidator()
    url_validator = validators.URLValidator()

    def __call__(self, value):
        if value.startswith('mailto://'):
            mail_to, email = value.rsplit('://', 1)
            self.email_validator(email)
        else:
            self.url_validator(value)


class LabPage(BasePage):
    subpage_types = ['RFPPage']
    parent_page_types = ['LabIndex']

    introduction = models.TextField(blank=True)
    icon = models.ForeignKey(
        'images.CustomImage',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL
    )
    lab_type = models.ForeignKey(
        'wagtailcore.Page',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='lab_public',
    )
    lab_link = models.CharField(blank=True, max_length=255, verbose_name='External link', validators=[MailToAndURLValidator()])
    link_text = models.CharField(max_length=255, help_text='Text to display on the button for external links', blank=True)
    body = StreamField(LabBlock())

    search_fields = BasePage.search_fields + [
        index.SearchField('introduction'),
        index.SearchField('body')
    ]

    content_panels = BasePage.content_panels + [
        ImageChooserPanel('icon'),
        FieldPanel('introduction'),
        MultiFieldPanel([
            PageChooserPanel('lab_type', 'funds.LabType'),
            FieldRowPanel([
                FieldPanel('lab_link'),
                FieldPanel('link_text'),
            ]),
        ], heading='Link for lab application'),
        StreamFieldPanel('body'),
        InlinePanel('related_pages', label="Related pages"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['rfps'] = self.get_children().live().public()
        return context

    can_open = True

    @property
    def is_open(self):
        try:
            return bool(self.lab_type.specific.open_round)
        except AttributeError:
            return bool(self.lab_link)

    def clean(self):
        if self.lab_type and self.lab_link:
            raise ValidationError({
                'lab_type': 'Cannot link to both a Lab page and external link',
                'lab_link': 'Cannot link to both a Lab page and external link',
            })

        if not self.lab_type and not self.lab_link:
            raise ValidationError({
                'lab_type': 'Please provide a way for applicants to apply',
                'lab_link': 'Please provide a way for applicants to apply',
            })

        if self.lab_type and self.link_text:
            raise ValidationError({
                'link_text': 'Cannot customise the text for internal lab pages, leave blank',
            })

        if self.lab_link and not self.link_text:
            raise ValidationError({
                'link_text': 'Please provide some text for the link button',
            })


class LabIndex(BasePage):
    subpage_types = ['LabPage']
    parent_page_types = ['home.HomePage']

    introduction = models.TextField(blank=True)

    content_panels = BasePage.content_panels + [
        FieldPanel('introduction')
    ]

    def get_context(self, request, *args, **kwargs):
        labs = LabPage.objects.live().public().descendant_of(self)

        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(labs, settings.DEFAULT_PER_PAGE)
        try:
            labs = paginator.page(page)
        except PageNotAnInteger:
            labs = paginator.page(1)
        except EmptyPage:
            labs = paginator.page(paginator.num_pages)

        context = super().get_context(request, *args, **kwargs)
        context.update(subpages=labs)
        return context
