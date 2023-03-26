from json_package.json_tool import write_to_json, load_from_json
name_of_file = 'quiz.json'


def init_file():
    write_to_json(name_of_file, [])


def add_summary(name_of_summary):
    data = load_from_json(name_of_file)
    data.append({
        'nameOfSummary': name_of_summary,
        'questions': [],
    })
    write_to_json(name_of_file, data)


def add_question(summary, question, answer):
    data = load_from_json(name_of_file)
    for topic in data:
        if summary == topic['nameOfSummary']:
            topic['questions'].append({
                'question': question,
                'answer': answer,
            })
    write_to_json(name_of_file, data)


if __name__ == '__main__':
    add_question('Теория вероятностей', 'Схемой Бернулли называется последовательность независимых испытаний, в каждом из которых возможны лишь два исхода — «успех» и «неудача», при этом успех в каждом испытании происходит с одной и той же вероятностью p∈(0,1) , а неудача — с вероятностью q=1−p?', True)
    add_question('Теория вероятностей',
                 'Геометрическое распределение — распределение дискретной случайной величины, равной количеству испытаний случайного эксперимента до наблюдения первого провала?',
                 False)
    add_question('Теория вероятностей',
                 'Нера́венство Ма́ркова в теории вероятностей не может дать оценку вероятности, что случайная величина превзойдет по модулю фиксированную положительную константу, в терминах её математического ожидания?',
                 False)
    add_question('Теория вероятностей',
                 'Нера́венство Ма́ркова в теории вероятностей не может дать оценку вероятности, что случайная величина превзойдет по модулю фиксированную положительную константу, в терминах её математического ожидания?',
                 False)
    add_question('Теория вероятностей',
                 'Утверждение E(a)=a, где a∈R — константа, а E - мат. ожидание верно?',
                 True)
