import datetime
import json
from urllib.parse import urlparse

import redis
from django.conf import settings
from django.http import HttpRequest
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.views import APIView

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


class VisitedLinks(APIView):

    def post(self, request: HttpRequest):
        '''
        Получает данные о посещенных сайтах и записывает их в БД Redis
        '''
        try:
            links = json.loads(request.body.decode('utf-8'))['links']
            time_point = datetime.datetime.now()
            domains = str()
            count = 0

            for link in links:
                count += 1
                if ('https://' or 'http://') in link:
                    domain = urlparse(link).hostname
                else:
                    domain = link

                if count <= (len(links) - 1):
                    domains += domain + ','
                else:
                    domains += domain
            redis_instance.set(time_point.timestamp(), domains)

            return Response(data={
                "status": "ok"
            }, status=HTTP_200_OK)
        except KeyError:
            return Response(data={
                "status": "Links отсутствует в теле запроса"
            }, status=HTTP_400_BAD_REQUEST)


class VisitedDomains(APIView):

    def get(self, request: HttpRequest):
        '''
        По временному промежутку, отдаёт посещенные сайты
        '''
        try:
            start_period = datetime.datetime.utcfromtimestamp(int(request.GET.get('from')))
            end_period = datetime.datetime.utcfromtimestamp(int(request.GET.get('to')))
            all_domains = list()
            for key in redis_instance.keys("*"):
                period = datetime.datetime.utcfromtimestamp(int(float(key.decode())))
                if start_period < period < end_period:
                    domain_list = redis_instance.get(key).decode().split(',')
                    for domain in domain_list:
                        if domain in all_domains:
                            continue
                        else:
                            all_domains.append(domain)
                else:
                    return Response(data={
                        "status": "В такой промежуток нет данных о посещениях"
                    }, status=HTTP_404_NOT_FOUND)
            data = {
                "domains": all_domains,
                "status": "ok"
            }

            return Response(data, status=HTTP_200_OK)
        except ValueError:
            return Response(data={
                "status": "Неверный формат даты. Укажите дату для 'from' и 'to' в формате datetime.timestamp"
            }, status=HTTP_400_BAD_REQUEST)
