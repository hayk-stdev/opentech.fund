import factory

from opentech.apply.funds.tests.factories import ApplicationSubmissionFactory
from opentech.apply.stream_forms.testing.factories import FormDataFactory
from opentech.apply.users.tests.factories import StaffFactory

from ...options import YES, NO, MAYBE, PRIVATE, REVIEWER
from ...models import Review, ReviewForm

from . import blocks

__all__ = ['ReviewFactory', 'ReviewFormFactory']


class ReviewFormDataFactory(FormDataFactory):
    field_factory = blocks.ReviewFormFieldsFactory


class ReviewFactory(factory.DjangoModelFactory):
    class Meta:
        model = Review

    class Params:
        recommendation_yes = factory.Trait(recommendation=YES)
        recommendation_maybe = factory.Trait(recommendation=MAYBE)
        draft = factory.Trait(is_draft=True)
        visibility_private = factory.Trait(visibility=PRIVATE)
        visibility_reviewer = factory.Trait(visibility=REVIEWER)

    submission = factory.SubFactory(ApplicationSubmissionFactory)
    revision = factory.SelfAttribute('submission.live_revision')
    author = factory.SubFactory(StaffFactory)
    form_fields = factory.LazyAttribute(lambda o: o.submission.round.review_forms.first().fields)
    form_data = factory.SubFactory(
        ReviewFormDataFactory,
        form_fields=factory.SelfAttribute('..form_fields'),
    )
    is_draft = False
    recommendation = NO
    score = 0


class ReviewFormFactory(factory.DjangoModelFactory):
    class Meta:
        model = ReviewForm

    name = factory.Faker('word')
    form_fields = blocks.ReviewFormFieldsFactory
