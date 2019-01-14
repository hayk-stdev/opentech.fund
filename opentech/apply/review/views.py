from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView

from wagtail.core.blocks import RichTextBlock

from opentech.apply.activity.messaging import messenger, MESSAGES
from opentech.apply.funds.models import ApplicationSubmission
from opentech.apply.review.blocks import RecommendationBlock, RecommendationCommentsBlock
from opentech.apply.review.forms import ReviewModelForm
from opentech.apply.stream_forms.models import BaseStreamForm
from opentech.apply.users.decorators import staff_required
from opentech.apply.utils.views import CreateOrUpdateView

from .models import Review


class ReviewContextMixin:
    def get_context_data(self, **kwargs):
        staff_reviews = self.object.reviews.by_staff().select_related('author')
        reviewer_reviews = self.object.reviews.by_reviewers().exclude(id__in=staff_reviews).select_related('author')
        return super().get_context_data(
            staff_reviews=staff_reviews,
            reviewer_reviews=reviewer_reviews,
            **kwargs,
        )


def get_fields_for_stage(submission):
    forms = submission.get_from_parent('review_forms').all()
    index = submission.workflow.stages.index(submission.stage)
    try:
        return forms[index].form.form_fields
    except IndexError:
        return forms[0].form.form_fields


@method_decorator(login_required, name='dispatch')
class ReviewCreateOrUpdateView(BaseStreamForm, CreateOrUpdateView):
    submission_form_class = ReviewModelForm
    model = Review
    template_name = 'review/review_form.html'

    def get_object(self, queryset=None):
        return self.model.objects.get(submission=self.submission, author=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        self.submission = get_object_or_404(ApplicationSubmission, id=self.kwargs['submission_pk'])

        if not self.submission.phase.permissions.can_review(request.user) or not self.submission.has_permission_to_review(request.user):
            raise PermissionDenied()

        if self.request.POST and self.submission.reviewed_by(request.user):
            return self.get(request, *args, **kwargs)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        has_submitted_review = self.submission.reviewed_by(self.request.user)
        return super().get_context_data(
            submission=self.submission,
            has_submitted_review=has_submitted_review,
            title="Update Review draft" if self.object else 'Create Review',
            **kwargs
        )

    def get_defined_fields(self):
        return get_fields_for_stage(self.submission)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['submission'] = self.submission

        if self.object:
            kwargs['initial'] = self.object.form_data

        return kwargs

    def form_valid(self, form):
        form.instance.form_fields = self.get_defined_fields()
        response = super().form_valid(form)

        if not self.object.is_draft:
            messenger(
                MESSAGES.NEW_REVIEW,
                request=self.request,
                user=self.object.author,
                submission=self.submission,
                related=self.object,
            )
        return response

    def get_success_url(self):
        return self.submission.get_absolute_url()


@method_decorator(login_required, name='dispatch')
class ReviewDetailView(DetailView):
    model = Review

    def dispatch(self, request, *args, **kwargs):
        review = self.get_object()
        user = request.user
        author = review.author

        if user != author and not (user.is_reviewer and review.reviewer_visibility) and not user.is_apply_staff:
            raise PermissionDenied

        if review.is_draft:
            return HttpResponseRedirect(reverse_lazy('apply:reviews:form', args=(review.submission.id,)))

        return super().dispatch(request, *args, **kwargs)


@method_decorator(staff_required, name='dispatch')
class ReviewListView(ListView):
    model = Review

    def get_queryset(self):
        self.submission = get_object_or_404(ApplicationSubmission, id=self.kwargs['submission_pk'])
        self.queryset = self.model.objects.filter(submission=self.submission, is_draft=False)
        return super().get_queryset()

    def should_display(self, field):
        return not isinstance(field.block, (RecommendationBlock, RecommendationCommentsBlock, RichTextBlock))

    def get_context_data(self, **kwargs):
        review_data = {}

        # Add the header rows
        review_data['title'] = {'question': '', 'answers': list()}
        review_data['score'] = {'question': 'Overall Score', 'answers': list()}
        review_data['recommendation'] = {'question': 'Recommendation', 'answers': list()}
        review_data['revision'] = {'question': 'Revision', 'answers': list()}
        review_data['comments'] = {'question': 'Comments', 'answers': list()}

        responses = self.object_list.count()

        for i, review in enumerate(self.object_list):
            review_data['title']['answers'].append('<a href="{}">{}</a>'.format(review.get_absolute_url(), review.author))
            review_data['score']['answers'].append(str(review.get_score_display()))
            review_data['recommendation']['answers'].append(review.get_recommendation_display())
            review_data['comments']['answers'].append(review.get_comments_display(include_question=False))
            if review.for_latest:
                revision = 'Current'
            else:
                revision = '<a href="{}">Compare</a>'.format(review.get_compare_url())
            review_data['revision']['answers'].append(revision)

            for field_id in review.fields:
                field = review.field(field_id)
                data = review.data(field_id)
                if self.should_display(field):
                    question = field.value['field_label']
                    review_data.setdefault(field.id, {'question': question, 'answers': [''] * responses})
                    review_data[field.id]['answers'][i] = field.block.render(None, {'data': data})

        return super().get_context_data(
            submission=self.submission,
            review_data=review_data,
            **kwargs
        )
