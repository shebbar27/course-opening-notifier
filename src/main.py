from time import sleep

import requests
from plyer import notification
from datetime import datetime

class_url_base = "https://eadvs-cscc-catalog-api.apps.asu.edu/catalog-microservices/api/v1/search/classes?"
reservation_url_base = "https://eadvs-cscc-catalog-api.apps.asu.edu/catalog-microservices/api/v1/search/reservedseatsadditionalinfo?"

required_courses = [
    'Knowledge Representation',
    'Software Requirements',
    'Statistical Learning Theory',
    'Modern Temporal Learning',
    'AI Safety',
    'Secure Microkernel',
]

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
    'classSection': '1001'
}

email_ids = ['sunaada.hebbar@asu.edu']


def build_url_str(parameters, url_base):
    url_str = url_base
    for parameter, value in parameters.items():
        url_str = url_str + str(parameter) + '=' + str(value) + '&'
    url_str = url_str[:-1]
    return url_str


def get_json_data(parameters, url_base):
    url = build_url_str(parameters, url_base)
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


def get_course_identifiers(data):
    class_number = -1
    course_id = -1
    classes = []
    if 'classes' in data:
        classes = data['classes']
    for clas in classes:
        if 'CLAS' in clas:
            class_data = clas['CLAS']
            if 'CLASSNBR' in class_data:
                class_number = class_data['CLASSNBR']
            if 'CRSEID' in class_data:
                course_id = class_data['CRSEID']
    return class_number, course_id


def get_available_count(data):
    for group in data:
        if 'descr' in group:
            if group['descr'] == "RC Master\'s Engin 1-3 courses":
                count = group['enrlCap'] - group['enrlTot']
                return count
    return -1


def notify(course, available_seats):
    title = "Course Availability"
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    message = f"{available_seats} seats opened up at {current_time} for {course} course!! Hurry up!!"
    notification.notify(
        title=title,
        message=message,
        timeout=10,
    )

    file = open("results.txt", "a")
    file.write(message + '\n')
    file.close()


def get_course_availability(courses):
    available_courses_info = {}
    for course in courses:
        params = combine_params(
            class_parameters,
            {
                'keywords': course,
            })
        data = get_json_data(params, class_url_base)
        class_number, course_id = get_course_identifiers(data)
        if class_number == -1 or course_id == -1:
            print(f"Course {course} Not Found")
        else:
            params = combine_params(
                reservation_parameters,
                {
                    'classNbr': class_number,
                    'crseId': course_id,
                })
            data = get_json_data(params, reservation_url_base)
            available_courses_info[course] = get_available_count(data)
    return available_courses_info


def main():
    available_courses_info = get_course_availability(required_courses)
    for course, available_seats in available_courses_info.items():
        if available_seats > 0:
            print(f"Course {course} has {available_seats} available seats")
            notify(course, available_seats)
        if available_seats == 0:
            print(f"Course {course} has NO seats available")
            # notify(course, available_seats)
        else:
            print(f"Reservation NOT available for the course {course}")


if __name__ == "__main__":
    while 1:
        main()
