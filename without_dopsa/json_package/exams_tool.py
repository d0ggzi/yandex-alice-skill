from json_package.json_tool import write_to_json, load_from_json


def add_exams():
    print("Введите количество добавляемых экзаменов")
    n = int(input())
    data = []
    for i in range(n):
        print("Введите название экзамена")
        name = str(input())
        print("Введите уч. группу")
        group = str(input())
        print("Введите дату проведения")
        date = str(input())
        print("Введите время проведения в 24 часовом формате")
        time = str(input())
        print("Введите место проведения")
        location = str(input())
        data.append({
            'nameExam': name,
            'studentGroup': group,
            'date': date,
            'time': time,
            'location': location,
        })
    write_to_json('exams.json', data)


if __name__ == '__main__':
    # add_exams()
    data = load_from_json('exams_example.json')
    write_to_json('exams_example.json', data)





