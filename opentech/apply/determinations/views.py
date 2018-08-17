from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView

from opentech.apply.activity.models import Activity
from opentech.apply.activity.messaging import messenger, MESSAGES
from opentech.apply.funds.models import ApplicationSubmission
from opentech.apply.funds.workflow import DETERMINATION_OUTCOMES
from opentech.apply.utils.views import CreateOrUpdateView, ViewDispatcher
from opentech.apply.users.decorators import staff_required

from .forms import ConceptDeterminationForm, ProposalDeterminationForm
from .models import Determination, TRANSITION_DETERMINATION, DeterminationMessageSettings, NEEDS_MORE_INFO


def get_form_for_stage(submission):
    forms = [ConceptDeterminationForm, ProposalDeterminationForm]
    index = submission.workflow.stages.index(submission.stage)
    return forms[index]


def determination_actions(user, submission):
    return [action[0] for action in submission.get_actions_for_user(user)]


def transition_from_outcome(outcome, submission):
    for transition_name in submission.phase.transitions:
        try:
            transition_type = TRANSITION_DETERMINATION[transition_name]
        except KeyError:
            pass
        else:
            if transition_type == outcome:
                return transition_name


def can_edit_determination(user, determination, submission):
    outcome = transition_from_outcome(determination.outcome, submission)
    valid_outcomes = determination_actions(user, submission)
    return outcome in valid_outcomes


def can_create_determination(user, submission):
    actions = determination_actions(user, submission)
    return any(action in DETERMINATION_OUTCOMES for action in actions)


@method_decorator(staff_required, name='dispatch')
class DeterminationCreateOrUpdateView(CreateOrUpdateView):
    model = Determination
    template_name = 'determinations/determination_form.html'

    def get_object(self, queryset=None):
        return self.model.objects.get(submission=self.submission)

    def dispatch(self, request, *args, **kwargs):
        self.submission = get_object_or_404(ApplicationSubmission, id=self.kwargs['submission_pk'])

        import pudb; pudb.set_trace()
        if not can_create_determination(request.user, self.submission):
            raise PermissionDenied()

        if self.submission.has_determination:
            messages.warning(request, _('A determination has already been submitted for that submission.'))
            return HttpResponseRedirect(reverse_lazy('apply:submissions:determinations:detail', args=(self.submission.id,)))

        try:
            determination = self.get_object()
        except Determination.DoesNotExist:
            pass
        else:
            if not can_edit_determination(request.user, determination, self.submission):
                messages.warning(request, _('There is a draft determination you do not have permission to edit.'))
                return HttpResponseRedirect(reverse_lazy('apply:submissions:determinations:detail', args=(self.submission.id,)))

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        determination_messages = DeterminationMessageSettings.for_site(self.request.site)

        return super().get_context_data(
            submission=self.submission,
            message_templates=determination_messages.get_for_stage(self.submission.stage.name),
            **kwargs
        )

    def get_form_class(self):
        return get_form_for_stage(self.submission)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['submission'] = self.submission
        kwargs['action'] = self.request.GET.get('action')
        return kwargs

    def get_success_url(self):
        return self.submission.get_absolute_url()

    def form_valid(self, form):
        response = super().form_valid(form)

        if not self.object.is_draft:
            messenger(
                MESSAGES.DETERMINATION_OUTCOME,
                request=self.request,
                user=self.object.author,
                submission=self.object.submission,
            )
            transition = transition_from_outcome(int(form.cleaned_data.get('outcome')), self.submission)

            if self.object.outcome == NEEDS_MORE_INFO:
                # We keep a record of the message sent to the user in the comment
                Activity.comments.create(
                    message=self.object.stripped_message,
                    user=self.request.user,
                    submission=self.submission,
                )

            self.submission.perform_transition(transition, self.request.user, request=self.request)

        return self.progress_stage(self.submission) or response

    def progress_stage(self, instance):
        try:
            instance.perform_transition('draft_proposal', self.request.user, request=self.request)
        except PermissionDenied:
            pass
        else:
            messenger(
                MESSAGES.INVITED_TO_PROPOSAL,
                request=self.request,
                user=self.request.user,
                submission=instance,
            )
            return HttpResponseRedirect(instance.get_absolute_url())


@method_decorator(staff_required, name='dispatch')
class AdminDeterminationDetailView(DetailView):
    model = Determination

    def get_object(self, queryset=None):
        return self.model.objects.get(submission=self.submission)

    def dispatch(self, request, *args, **kwargs):
        self.submission = get_object_or_404(ApplicationSubmission, id=self.kwargs['submission_pk'])
        determination = self.get_object()

        if can_edit_determination(request.user, determination, self.submission) and determination.is_draft:
            return HttpResponseRedirect(reverse_lazy('apply:submissions:determinations:form', args=(self.submission.id,)))

        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class ApplicantDeterminationDetailView(DetailView):
    model = Determination

    def get_object(self, queryset=None):
        return self.model.objects.get(submission=self.submission)

    def dispatch(self, request, *args, **kwargs):
        self.submission = get_object_or_404(ApplicationSubmission, id=self.kwargs['submission_pk'])
        determination = self.get_object()

        if request.user != self.submission.user:
            raise PermissionDenied

        if determination.is_draft:
            return HttpResponseRedirect(reverse_lazy('apply:submissions:determinations:detail', args=(self.submission.id,)))

        return super().dispatch(request, *args, **kwargs)


class DeterminationDetailView(ViewDispatcher):
    admin_view = AdminDeterminationDetailView
    applicant_view = ApplicantDeterminationDetailView
