import requests
from plyer import notification
from datetime import datetime

class_url_base = "https://eadvs-cscc-catalog-api.apps.asu.edu/catalog-microservices/api/v1/search/classes?"

required_courses = [
    'Knowledge Representation',
    'Mobile Computing',
    'Semantic Web Mining',
    'Data Visualization',
]

class_parameters = {
    'refine': 'Y',
    'campusOrOnlineSelection': 'A',
    'searchType': 'all',
    'term': '2221',
    'subject': 'CSE',
    'honors': 'F',
    'promod': 'F',
    'level': 'grad',
    'campus': 'TEMPE',
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


def get_available_class_info(data):
    classes = []
    class_details = {}
    if 'classes' in data:
        classes = data['classes']
    if len(classes) != 0:
        for clas in classes:
            if 'CLAS' in clas:
                class_data = clas['CLAS']
                count = int(class_data["ENRLCAP"]) - int(class_data["ENRLTOT"])
                class_number = class_data["CLASSNBR"]
                class_details[class_number] = count
    return class_details


def notify(course, course_number, available_seats):
    title = "Course Availability"
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    message = f"{available_seats} seats opened up at {current_time} for {course} : {course_number} course!! Hurry up!!"
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
        info = get_available_class_info(data)
        if len(info.items()) != 0:
            available_courses_info[course] = info
        else:
            print(f"Reservation NOT available for the course {course}")
    return available_courses_info


def main():
    available_courses_info = get_course_availability(required_courses)
    for course, course_info in available_courses_info.items():
        course_numbers = course_info.keys()
        for course_number in course_numbers:
            available_seats = course_info[course_number]
            if available_seats > 0:
                print(f"Course {course} : {course_number} has {available_seats} available seats")
                notify(course, course_number, available_seats)
            if available_seats == 0:
                print(f"Course {course} : {course_number} has NO seats available")
                # notify(course, available_seats)


if __name__ == "__main__":
    while 1:
        main()
