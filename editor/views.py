from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, ListView, UpdateView, DeleteView

from editor.forms import TopicForm, WordFilterForm, WordCreateForm, WordUpdateForm
from quizzes.models import Word, Topic


class TeachersOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_teacher


class TopicCreateView(TeachersOnlyMixin, FormView):
    template_name = 'editor/topic_form.html'
    form_class = TopicForm
    created_topic = None

    def get_success_url(self):
        # redirect teacher to the add words page if new topic created successfully
        return reverse('topic_words', kwargs={'topic_id': self.created_topic.id})

    def form_valid(self, form):
        self.created_topic = form.save()
        messages.success(self.request, "Topic created successfully!")
        return super().form_valid(form)


class TopicWordsView(TeachersOnlyMixin, ListView):
    model = Word
    template_name = 'editor/topic_words.html'
    context_object_name = 'words'

    def get_queryset(self):
        qs = Word.objects.order_by(Lower('origin'))
        topic_id = self.kwargs.get('topic_id', None)

        # if user is visiting a topic-specific page, show them only words from that topic
        if topic_id:
            topic = get_object_or_404(Topic, pk=self.kwargs.get('topic_id'))
            qs = Word.objects.filter(topics=topic).order_by(Lower('origin'))

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic_id = self.kwargs.get('topic_id', None)
        context['topic_id'] = topic_id

        if topic_id is None:
            context['word_filter_form'] = WordFilterForm()

        # store the most recently visited topic to enable the user to be redirected back here later.
        self.request.session['recent_topic'] = topic_id
        return context


@user_passes_test(lambda user: user.is_authenticated and user.is_teacher)
def add_word(request, topic_id=None):
    """ Obtain (and validate) the HTML form to add a new word """
    data = dict()

    # Process a completed new Word form
    if request.method == 'POST':
        form = WordCreateForm(request.POST)
        if form.is_valid():
            new_word = form.save()

            if topic_id is not None:
                topic = get_object_or_404(Topic, pk=topic_id)
                new_word.topics.add(topic)
                words = Word.objects.filter(topics=topic).order_by(Lower('origin'))
            else:
                # words assigned to no topics
                words = Word.objects.filter(topics__isnull=True).order_by(Lower('origin'))
            data['is_valid'] = True

            data['html_word_rows'] = render_to_string('editor/word_list.html', {'words': words})

        else:
            data['is_valid'] = False

    # Otherwise, create a new blank Word form
    else:
        form = WordCreateForm()

    context = {'form': form}
    data['html_form'] = render_to_string('editor/word_include_form.html', context, request=request)
    return JsonResponse(data)


@user_passes_test(lambda user: user.is_authenticated and user.is_teacher)
def get_filtered_words(request):
    # get base queryset
    words = Word.objects.order_by(Lower('origin'))

    # extract filter options from GET request
    search = request.GET.get('search', None)
    topic_id = request.GET.get('topic', None)

    # apply filters
    if search is not None:
        words = words.filter(Q(origin__icontains=search) | Q(target__icontains=search))
    if topic_id is not None:
        # special case for Words with no associated Topics
        if topic_id == "-1":
            words = words.filter(topics__isnull=True)
        elif topic_id != "":
            filter_topic = get_object_or_404(Topic, pk=topic_id)
            words = words.filter(topics=filter_topic)

    data = dict()
    data['html_word_rows'] = render_to_string('editor/word_list.html', {'words': words})
    return JsonResponse(data)


class WordUpdateView(TeachersOnlyMixin, UpdateView):
    model = Word
    form_class = WordUpdateForm
    template_name = 'editor/word_form.html'

    def get_success_url(self):
        # redirect teacher to the most recently-visited add words page after updating a word
        recent_topic = self.request.session.get('recent_topic', None)
        if recent_topic:
            url = reverse('topic_words', kwargs={'topic_id': recent_topic})
        else:
            url = reverse('topic_words')
        return url


class TopicUpdateView(TeachersOnlyMixin, UpdateView):
    model = Topic
    form_class = TopicForm
    template_name = 'editor/topic_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, "Topic updated successfully!")
        return super().form_valid(form)


class TopicDeleteView(TeachersOnlyMixin, DeleteView):
    model = Topic
    success_url = reverse_lazy('home')
    template_name = "editor/topic_confirm_delete.html"

    def form_valid(self, form):
        messages.success(self.request, "Topic deleted successfully!")
        return super().form_valid(form)


class WordDeleteView(TeachersOnlyMixin, DeleteView):
    model = Word
    success_url = reverse_lazy('home')
    template_name = "editor/word_confirm_delete.html"

    def get_success_url(self):
        # redirect teacher to the most recently-visited add words page after deleting a word
        recent_topic = self.request.session.get('recent_topic', None)
        if recent_topic:
            url = reverse('topic_words', kwargs={'topic_id': recent_topic})
        else:
            url = reverse('topic_words')
        return url
