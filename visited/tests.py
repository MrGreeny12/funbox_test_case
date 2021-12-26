import json

import redis
from django.conf import settings
from django.test import TestCase


redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


class TestViews(TestCase):
    '''
    Тестирует работу представлений
    '''

    def setUp(self) -> None:
        self.correct_data = json.dumps({
            "links": [
                "https://ya.ru",
                "https://ya.ru?q=123",
                "funbox.ru",
                "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor"
            ]
        })
        self.incorrect_data = json.dumps({
            "lunks": [
                "https://ya.ru",
                "https://ya.ru?q=123",
                "funbox.ru",
                "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor"
            ]
        })
        self.correct_start_date = 1545221231
        self.correct_end_date = 1640380228
        self.incorrect_start_date = '12.10.2020'
        self.data = redis_instance.set(1545221231, "ya.ru,funbox.ru,stackoverflow.com")

    def test_correct_income_links_list(self):
        response = self.client.post('/api/v1/visited_links/', data=self.correct_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_incorrect_income_links_list(self):
        response = self.client.post('/api/v1/visited_links/', data=self.incorrect_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_correct_get_links_list(self):
        response = self.client.get(f'/api/v1/visited_domains/',
                                   {'from': self.correct_start_date, 'to': self.correct_end_date})

        self.assertEqual(response.status_code, 200)

    def test_incorrect_get_links_list(self):
        response1 = self.client.get(f'/api/v1/visited_domains/',
                                   {'from': self.correct_end_date, 'to': self.correct_end_date})
        response2 = self.client.get(f'/api/v1/visited_domains/',
                                    {'from': self.incorrect_start_date, 'to': self.correct_end_date})

        self.assertEqual(response2.status_code, 400)
        self.assertEqual(response1.status_code, 404)
