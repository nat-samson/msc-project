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
    """Mixin that determines if a user is a) logged in, b) a teacher. Raises Access Denied error if not."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_teacher


class TopicWordsView(TeachersOnlyMixin, ListView):
    """View for listing all the Words in a specified Topic, or all Words across all Topics."""
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

        # store the most recently visited topic to enable the user to be sent back here after adding/editing a word
        topic_id = self.kwargs.get('topic_id', '')
        context['topic_id'] = topic_id

        # if user is on the 'All Topics' page, display the filter form
        if topic_id == '':
            context['word_filter_form'] = WordFilterForm()

        return context


@user_passes_test(lambda user: user.is_authenticated and user.is_teacher)
def add_word(request, topic_id=None):
    """Obtain (and validate) the HTML form to add a new word as a JSON file."""
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

            data['html_word_rows'] = render_to_string('editor/word_list.html', {'words': words, 'topic_id': topic_id})

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
    """Get the Words data for the table on the All Topics page as a JSON, according to the URL parameters."""
    # get base queryset
    words = Word.objects.order_by(Lower('origin'))

    # extract filter options from GET request (i.e. the URL parameters)
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


class TopicCreateView(TeachersOnlyMixin, FormView):
    """View for creating a new Topic based on the TopicForm."""
    template_name = 'editor/topic_form.html'
    form_class = TopicForm
    created_topic = None

    def get_success_url(self):
        # redirect teacher to the add words page if new topic created successfully
        return reverse('topic_words', kwargs={'topic_id': self.created_topic.id})

    def form_valid(self, form):
        self.created_topic = form.save()
        # show a message on the homepage if successful
        messages.success(self.request, "Topic created successfully!")
        return super().form_valid(form)


class TopicUpdateView(TeachersOnlyMixin, UpdateView):
    """View for updating a specified Topic."""
    model = Topic
    form_class = TopicForm
    template_name = 'editor/topic_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, "Topic updated successfully!")
        return super().form_valid(form)


class TopicDeleteView(TeachersOnlyMixin, DeleteView):
    """View for deleting a specified Topic."""
    model = Topic
    success_url = reverse_lazy('home')
    template_name = "editor/topic_confirm_delete.html"

    def form_valid(self, form):
        messages.success(self.request, "Topic deleted successfully!")
        return super().form_valid(form)


class WordUpdateView(TeachersOnlyMixin, UpdateView):
    """View for updating a specified Word."""
    model = Word
    form_class = WordUpdateForm
    template_name = 'editor/word_form.html'

    def get_success_url(self):
        # redirect teacher to the most recently-visited add words page after updating a word
        next_topic = self.request.GET.get('next')

        if next_topic:
            url = reverse('topic_words', kwargs={'topic_id': next_topic})
        else:
            url = reverse('topic_words')
        return url


class WordDeleteView(TeachersOnlyMixin, DeleteView):
    """View for deleting a specified Word."""
    model = Word
    template_name = "editor/word_confirm_delete.html"

    def get_success_url(self):
        # redirect teacher to the most recently-visited add words page after deleting a word
        next_topic = self.request.GET.get('next')

        if next_topic:
            url = reverse('topic_words', kwargs={'topic_id': next_topic})
        else:
            url = reverse('topic_words')
        return url
