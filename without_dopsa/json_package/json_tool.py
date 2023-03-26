import json
import difflib
import re


count_of_elements = 3
delta_summary = 0.05
delta_topic = 0.05

subject_list = [
    "Алгоритмы и структуры данных",
    "Дискретная математика",
    "Язык программирования Java",
    "Машинное обучение",
    "Теория вероятностей"
]

def similarity(s1: str, s2: str):
    normalized1 = s1.lower()
    normalized2 = s2.lower()
    matcher = difflib.SequenceMatcher(None, normalized1, normalized2)
    return matcher.ratio()


def write_to_json(name_of_file: str, data: list):
    json_data = json.dumps(data, indent=4, ensure_ascii=False)
    with open(name_of_file, 'w', encoding='UTF-8') as file:
        file.write(json_data)


def load_from_json(name_of_file: str):
    with open(name_of_file, 'r', encoding='UTF-8') as file:
        dict = json.loads(file.read())
    return dict

def get_link_from_topic_list(name_of_summary: str, name_of_topic: str):
    answer = []
    data = load_from_json('json_package/result_data.json')
    for summary in data:
        if summary['nameOfSummary'] == name_of_summary:
            for topic in summary['topicsOfSummary']:
                answer.append([similarity(topic['nameOfTopic'], name_of_topic), topic['linkOfTopic']])
                if len(answer) == 4:
                    answer.sort(reverse=True)
                    answer.pop()
            break
    for index in range(len(answer) - 1, -1, -1):
        if answer[0][0] - answer[index][0] > delta_summary or answer[index][0] < 0.5:
            answer.pop(index)
    return answer


def get_themes_of_subject(name_of_subject: str):
    themes = []
    data = load_from_json('json_package/result_data.json')
    for summary in data:
        if summary['nameOfSummary'] == name_of_subject:
            for topic in summary['topicsOfSummary']:
                themes.append(topic['nameOfTopic'])
            break
    return themes

def get_question(name_of_subject: str, id: int):
    data = load_from_json('json_package/quiz.json')
    for summary in data:
        if summary['nameOfSummary'] == name_of_subject:
            ques = summary['questions'][id-1]
            if ques.get('answer', 2) != 2:
                return ques['question'], ques['answer'], False
            return ques['question'], ques['answers'], True
        
def get_number_of_questions(name_of_subject: str):
    data = load_from_json('json_package/quiz.json')
    for summary in data:
        if summary['nameOfSummary'] == name_of_subject:
            return len(summary['questions'])


def get_ticket(subject: str, id: int):
    data = load_from_json('json_package/tickets.json')
    for summary in data:
        if summary['subject'] == subject:
            return summary['tickets'][id-1]['text']

def get_exams(group: str):
    data = load_from_json('json_package/exams.json')
    for exams in data:
        if exams['studentGroup'] == group:
            return exams['exams']
        
def get_groups():
    data = load_from_json('json_package/exams.json')
    groups = []
    for exams in data:
        groups.append(exams['studentGroup'])
    return groups
        
def get_group_name(text: str):
    regex = r'\b[PRLDVNTKMUGZH]\d+\b'
    matches = re.findall(regex, text)
    return matches


if __name__ == '__main__':
    probable_topic = get_link_from_topic_list(name_of_summary="Язык программирования Java",
                                                name_of_topic='хз')
    if len(probable_topic) == 1:
        print(probable_topic)
    else:
        print(probable_topic)
        # действие, если под запрос пользователя подходит несколько вариантов

    # print('\n'.join("- " + el for el in get_themes_of_subject("Дискретная математика")[:20]))
    print(get_exams('R32362'))
    print(get_group_name('расписание у группы R32362, пожалуйста R3138'))

