from django.test import SimpleTestCase

from quizzes.templatetags.quiz_extras import results_reaction, get_filtered_list_url


class QuizTemplateTagTests(SimpleTestCase):
    def test_results_reaction_great(self):
        reaction = results_reaction(12, 12)
        self.assertEquals(reaction, ("Congratulations! ", "🏆"))

    def test_results_reaction_good(self):
        reaction = results_reaction(6, 12)
        self.assertEquals(reaction, ("Nicely done. ", "😎"))

    def test_results_reaction_bad(self):
        reaction = results_reaction(5, 12)
        self.assertEquals(reaction, ("Keep at it! ", "📚"))

    def test_results_reaction_divide_by_zero(self):
        reaction = results_reaction(0, 0)
        self.assertEquals(reaction, ("Divide by zero error! ", "❓"))

    def test_get_filtered_list_url(self):
        topic_id = 1
        url = get_filtered_list_url(topic_id)
        self.assertEquals(url, "/admin/quizzes/word/?topics__id__exact=1")
