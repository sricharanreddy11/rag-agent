from django.test import TestCase

from university_agent.utils import identify_creation_intent_and_execute


# Create your tests here.
def test_creation_agent():
    identify_creation_intent_and_execute(user_query="Create a task to Complete the project by next week")