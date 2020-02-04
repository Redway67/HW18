import requests
from datetime import datetime
from modules.data_base import add_records

DOMAIN = 'https://api.hh.ru/'
URL_VACANCIES = f'{DOMAIN}vacancies'
URL_AREA = f'{DOMAIN}suggests/areas'


def parser(vacancy='Python developer', region='Москва'):
    req = []
    skills = {}
    total = 0
    qnt_skills = 0
    # по умолчанию info
    area = '1'  # код Москвы
    info = {'region': region, 'vacancy': vacancy, 'found': 0, 'data': datetime.today().strftime("%d/%m/%Y"),
            'requirement': req}  # передаем в html
    # находим код региона для последущего запроса
    if region != 'Москва':
        params = {'text': f'{region}'}
        ra = requests.get(URL_AREA, params=params)
        if ra.status_code == 200:
            area_result = ra.json()
            if area_result['items']:
                area = area_result['items'][0]['id']
            else:
                print('Такого региона нет!')
                # TODO: вывести  сообщение, потом ?
    par = {'text': vacancy, 'area': area}
    rv = requests.get(URL_VACANCIES, params=par)
    if rv.status_code == 200:
        result = rv.json()
        info['found'] = result['found']
        # идем по страницам и считаем навыки
        # TODO : нужен прогресс-бар
        if result['items']:
            for p in range(1 + (info['found'] // 20)):
                params = {'text': vacancy, 'area': area, 'page': p}
                res = requests.get(URL_VACANCIES, params=params).json()
                # страница {p}
                for j in res['items']:
                    resj = requests.get(j['url']).json()
                    for i in resj['key_skills']:
                        if i['name'] in skills:
                            skills[i['name']] += 1
                        else:
                            skills.setdefault(i['name'], 1)
                            qnt_skills += 1
                        total += 1
            # статистика
            for k, v in sorted(skills.items(), key=lambda x: int(x[1]), reverse=True):
                skill = {'name': k, 'count': v, 'percent': round(v / total * 100, 2)}  # в формате как в задании
                req.append(skill)

            info['requirement'] = req
            # сохраняем в файл запрос и результат
            add_records(info)
        else:
            # TODO: вывести  сообщение, потом ?
            print(f'В регионе {region} вакансии {vacancy} не найдено.')
    else:
        # TODO: вывести  сообщение, потом ?
        print('Ошибка поиска!')

    return info
