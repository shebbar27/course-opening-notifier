import json

import requests

class_url_base = 'https://eadvs-cscc-catalog-api.apps.asu.edu/catalog-microservices/api/v1/search/classes?'
reservation_url_base = 'https://eadvs-cscc-catalog-api.apps.asu.edu/catalog-microservices/api/v1/search/reservedseatsadditionalinfo?'

class_parameters = {
    'refine': 'Y',
    'campusOrOnlineSelection': 'A',
    'searchType': 'all',
    'term': '2221',
    'subject': 'CSE',
    'campus': 'TEMPE',
    'honors': 'F',
    'promod': 'F',
    'level': 'grad'
}

reservation_parameters = {
    'term': '2221',
    'sessionCode': 'C',
    'classType': 'E',
    'acadCareer': 'GRAD',
    'crseOfferNbr': '1',
}

course_ids = {
    '573',
    '578',
    '579',
}


def main():
    def build_url_str(parameters,url_base):
        url_str = url_base
        for parameter, value in parameters.items():
            url_str = url_str + str(parameter) + '=' + str(value) + '&'
        url_str = url_str[:-1]
        return url_str

    def get_json_data(parameters, url_base):
        url = build_url_str(parameters, url_base)
        print(url)
        r = requests.get(url, headers={'authorization': 'Bearer null'})
        if r.status_code == 200:
            return r.json()
        else:
            print(str(r.status_code) + ' Error')
            return {}

    def combine_params(given_parameters, new_parameters):
        params = given_parameters
        for key, value in new_parameters.items():
            params[str(key)] = str(value)
        return params

    def get_class_number(data):
        return '26252'

    def get_course_id(data):
        return '127813'

    def get_available_count(data):
        return 1

    def get_course_availability(courses):
        availabilty = {}
        for course in courses:
            params = combine_params(
                class_parameters,
                {
                    'catalogNbr': course,
                })
            data = get_json_data(params, class_url_base)
            classNbr = get_class_number(data)
            crseId = get_course_id(data)
            params = combine_params(
                reservation_parameters,
                {
                    'classNbr': classNbr,
                    'crseId': crseId,
                })
            data = get_json_data(params, reservation_url_base)
            availabilty[course] = get_available_count(data)
        return availabilty

    available_courses = get_course_availability(course_ids)
    for course, availability in available_courses.items():
        print('Course :' + course + ' has ' + str(availability) + ' available open seats')


if __name__ == "__main__":
    main()
