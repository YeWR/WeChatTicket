from django.test import TestCase
from .. import views as views

class AnimalTestCase(TestCase):

    def test_animals_can_speak(self):
        """add test demo"""
        testNum = 4
        x = []
        y = []
        ans = []
        for i in range(0, testNum):
            x.append(i)
            y.append(2 * i)
            ans.append(3 * i)
        for i in range(0, testNum):
            self.assertEqual(views.testDemoAdd(x[i], y[i]), ans[i])
