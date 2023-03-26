import inspect
import sys
from abc import ABC, abstractmethod
from typing import Optional
from random import choice, randint
import text_config
from multiprocessing import Process

from states import STATE_RESPONSE_KEY
from request import Request
import intents
from database import DataBase
from json_package.teachers import get_teacher_schedule, found_teachers_link
from json_package.json_tool import get_link_from_topic_list, get_themes_of_subject, subject_list, get_number_of_questions, get_question, get_ticket, get_groups, get_exams, get_group_name

database = DataBase()

def button(title, payload=None, url=None, hide=False):
    button = {
        'title': title,
        'hide': hide,
    }
    if payload is not None:
        button['payload'] = payload
    if url is not None:
        button['url'] = url
    return button


def get_name_of_subject(name: str):
    if name == "algorithms":
        return "Алгоритмы и структуры данных"
    elif name == "discrete_math":
        return "Дискретная математика"
    elif name == "programming":
        return 	"Язык программирования Java"
    elif name == "machine_learning":
        return "Машинное обучение"
    elif name == "probability_theory":
        return "Теория вероятностей"
    return False

def get_teacher(name: str):
    if name == "algorithms":
        return "Алгоритмы и структуры данных", "Елизавета Васильевна", "1521359/f1af75f950bf37af3711", True
    elif name == "discrete_math":
        return "Дискретная математика", "Данила Валерьевич", "213044/8f653c1af4f37d7c15d2", False
    elif name == "programming":
        return 	"Язык программирования Java", "Ева Дмитриевна", "1521359/8c4d769ebdddc2fcba9e", True
    elif name == "machine_learning":
        return "Машинное обучение", "Никита Сергеевич", "1540737/29667d29e1b1bf929c2f", False
    elif name == "probability_theory":
        return "Теория вероятностей", "Максим Сергеевич", "213044/4a1fe1d5a3bbcb5f349f", False
    return False

class Scene(ABC):

    @classmethod
    def id(cls):
        return cls.__name__

    """Генерация ответа сцены"""
    @abstractmethod
    def reply(self, request):
        raise NotImplementedError()

    """Проверка перехода к новой сцене"""
    def move(self, request: Request):
        if intents.REPEAT in request.intents:
            return self
        next_scene = self.handle_local_intents(request)
        if next_scene is None:
            next_scene = self.handle_global_intents(request)
        return next_scene

    @abstractmethod
    def handle_global_intents(self):
        raise NotImplementedError()

    @abstractmethod
    def handle_local_intents(request: Request) -> Optional[str]:
        raise NotImplementedError()

    def fallback(self, request: Request):
        buttons = [button('Что ты умеешь?', hide=True), button('Помощь', hide=True)]
        return self.make_response('Извините, я вас не понял. Пожалуйста, попробуйте переформулировать вопрос.', buttons=buttons)

    def make_response(self, text, tts=None, card=None, state=None, buttons=None, directives=None, end_session=False):
        response = {
            'text': text,
            'tts': tts if tts is not None else text,
            'end_session': end_session,
        }
        if card is not None:
            response['card'] = card
        if buttons is not None:
            response['buttons'] = buttons
        # if directives is not None:
        #     response['directives'] = directives
        webhook_response = {
            'response': response,
            'version': '1.0',
            STATE_RESPONSE_KEY: {
                'scene': self.id(),
            },
        }
        if state is not None:
            webhook_response[STATE_RESPONSE_KEY].update(state)
            # webhook_response[STATE_RESPONSE_KEY]['scene'] = self.id()
        return webhook_response
    
class WithoutDopsaScene(Scene):
    def handle_global_intents(self, request: Request):
        if intents.HELP in request.intents: 
            return Help()
        elif intents.CAN_DO in request.intents: 
            return CanDo()
        elif intents.EXAMS_SCHEDULE in request.intents:
            return AskGroup()
        elif intents.FOUND_TEACHER in request.intents:
            return FoundTeacher()
        elif intents.NOTES in request.intents or intents.EXAM in request.intents or intents.TICKET in request.intents:
            return AskSubject()
        elif intents.NOTES_WITH_SUBJECT in request.intents:
            return AskTheme()
        elif intents.EXAM_WITH_SUBJECT in request.intents:
            return StartExam()
        elif intents.TICKET_WITH_SUBJECT in request.intents:
            return SendTickets()
        elif intents.STOP_SESSION in request.intents:
            return StopSession()
        elif intents.THANKS in request.intents:
            return Thanks()
        elif intents.HELLO in request.intents:
            return Hello()
        else:
            text = request.request_body['request']['original_utterance']
            if "расписание" in text:
                groups = get_group_name(text)
                groups_exist = get_groups()
                for group in groups:
                    if group in groups_exist:
                        request.state['group'] = group
                        return SendSchedule()
                return AskGroup()
        
        
class StopSession(WithoutDopsaScene):
    def reply(self, request: Request):
        text = "Вы уверены, что хотите выйти?"
        card = {
            "type": "BigImage",
            "image_id": '1521359/33c165dae36d35b8ffce',
            "title": 'Вы уверены?',
            "description": "Уже уходите?",
        }
        return self.make_response(text, buttons=[button("Да"), button("Нет")], card=card)
    
    def handle_local_intents(self, request: Request):
        if intents.POSITIVE_RESP in request.intents:
            return StopSessionSure()
        elif intents.NEGATIVE_RESP in request.intents:
            return ContinueSession()

class StopSessionSure(WithoutDopsaScene):
    def reply(self, request: Request):
        text = "Мы будем скучать!"
        return self.make_response(text, end_session=True)
    
    def handle_local_intents(self, request: Request):
        pass

class ContinueSession(WithoutDopsaScene):
    def reply(self, request: Request):
        text = "Вы уверены, что хотите выйти?"
        card = {
            "type": "BigImage",
            "image_id": '1652229/0a2bc601ab052059300d',
            "title": 'Ура!',
            "description": "С возвращением!",
        }
        return self.make_response(text, card=card)
    
    def handle_local_intents(self, request: Request):
        pass

class Help(WithoutDopsaScene):
    def reply(self, request: Request):
        text = 'Доступные команды в навыке: \n \
        «пришли конспект» - для получения конспекта; \n \
        «отправь билет» - для получения случайного билета; \n \
        «начни экзамен» - для запуска викторины; \n \
        «отправь расписание» - для показа расписания экзаменов вашей группы; \n \
        «найти препода» - чтобы увидеть где и когда будет преподаватель ; \n \
        «хватит» - для прекращения сеанса; \n \
        «повтори» - повторение предыдущей фразы.'
        return self.make_response(text, state=request.state)
    
    def handle_local_intents(self, request: Request):
        pass

class CanDo(WithoutDopsaScene):
    def reply(self, request: Request):
        text = 'Я могу прислать конспект, отправить случайный билет, провести викторину по выбранной Вами теме, найти расписание ваших экзаменов или \
                показать когда и где поймать препода. Для этого напишите "пришли конспект", "отправь билет", "начни экзамен", "отправь расписание" или "найти препода"'
        buttons = [button('Пришли конспект'), button('Отправь билет'), button('Начни экзамен'), button('Найти препода'), button('Отправь расписание экзаменов'), ]

        return self.make_response(text, buttons = buttons, state=request.state)
    
    def handle_local_intents(self, request: Request):
        pass

class Thanks(WithoutDopsaScene):
    def reply(self, request: Request):
        text = choice(text_config.thanks_text)
        return self.make_response(text, state=request.state)
    
    def handle_local_intents(self, request: Request):
        pass

class Hello(WithoutDopsaScene):
    def reply(self, request: Request):
        text = 'Привет-привет'
        return self.make_response(text, state=request.state)
    
    def handle_local_intents(self, request: Request):
        pass


class FoundTeacher(WithoutDopsaScene):
    def reply(self, request: Request):
        text = 'Введите ФИО преподавателя \n'
        
        state = request.state
        state['choose'] = intents.FOUND_TEACHER
        state['scene'] = self.id()

        return self.make_response(text, state=state)
    
    def handle_local_intents(self, request: Request):
        return SendTeacher()
    
    def fallback(self, request: Request):
        buttons = [button('Что ты умеешь?', hide=True), button('Помощь', hide=True)]
        return self.make_response('Не могу найти такого преподавателя', buttons=buttons, state=request.state)


def get_teacher_schedule_process(request: Request):
    database = DataBase()
    request_text = request.request_body['request']['original_utterance']
    teacher_link, teacher_name = found_teachers_link(request_text)
    if not teacher_link:
        database.update_answer(request.request_body['session']['user_id'], "")
        return False
    teacher = get_teacher_schedule(teacher_link['href'])
    text = f"{teacher_name} \nКогда и где найти преподавателя: \n"
    for day in teacher.keys():
        text += day + '\n'
        for element in teacher[day]:
            text += "   " + element['time'] + ' | ' + element['room'] + '\n'

    database.update_answer(request.request_body['session']['user_id'], text[:1024])
    database.close_conn()

class SendTeacher(WithoutDopsaScene):
    def reply(self, request: Request):
        global database
        buttons = None
        tts = None
        state = request.state
        state['choose'] = intents.FOUND_TEACHER
        if intents.READY in request.intents:
            answer = database.get_answer(request.request_body['session']['user_id'])
            if len(answer) > 0:
                text = answer
            else:
                text = "Не могу найти такого преподавателя"
                buttons=[button("Попробовать снова", hide=True)]
        else:
            process = Process(target = get_teacher_schedule_process, args=(request,)) 
            process.start()

            text = "Поиск преподавателя... Поиск расписания...\nЧерез 5 секунд скажите «Готово», чтобы увидеть результат."
            tts = "Поиск преподавателя sil <[1000]> Поиск расписания sil <[1000]> Через 5 секунд скажите «Готово», чтобы увидеть результат"
            buttons=[button("Готово", hide=True)]
        state['scene'] = self.id()

        return self.make_response(text, state=state, buttons=buttons)
    
    def handle_local_intents(self, request: Request):
        if intents.READY in request.intents:
            return SendTeacher()
        elif intents.NEGATIVE_RESP in request.intents or intents.AGAIN in request.intents:
            return FoundTeacher()
        
    def fallback(self, request: Request):
        text = "Не понял Вас, попробуйте найти преподавателя снова"
        buttons=[button("Попробовать снова", hide=True)]
        return self.make_response(text, buttons=buttons)


class StartExam(WithoutDopsaScene):
    def reply(self, request: Request):
        text = 'Отлично! Начинаем экзамен?'
        state = request.state
        state['choose'] = intents.EXAM
        if not intents.REPEAT in request.intents:
            intent = intents.SUBJECT if intents.SUBJECT in request.intents else intents.EXAM_WITH_SUBJECT
            state['subject'] = request.intents[intent]['slots']['subject']['value']
        state['scene'] = self.id()

        subject_name, teacher_name, teacher_photo, female = get_teacher(state['subject'])
        text += f"Меня зовут {teacher_name} и я проведу тебе экзамен по предмету {subject_name} \n" 
        if female: description = f"Меня зовут {teacher_name}, я преподаватель по предмету {subject_name}. Но экзамен тебе проведёт мой ассистент Кирилл"
        else: description = f"Меня зовут {teacher_name} и я проведу тебе экзамен по предмету {subject_name}."
        card = {
            "type": "BigImage",
            "image_id": teacher_photo,
            "title": 'Отлично! Начинаем экзамен?',
            "description": description,
        }

        return self.make_response(text, buttons=[button("Да"), button("Нет")], state=state, card=card)
    
    def handle_local_intents(self, request: Request):
        if intents.POSITIVE_RESP in request.intents:
            return Exam()
        else:
            return NoExam()
        
class NoExam(WithoutDopsaScene):
    def reply(self, request: Request):
        text = 'Хорошо, выход из экзамена.'
        buttons = [button('Что ты умеешь?', hide=True), button('Помощь', hide=True)]
        return self.make_response(text, buttons=buttons)
    
    def handle_local_intents(self, request: Request):
        pass

class Exam(WithoutDopsaScene):
    def reply(self, request: Request):
        state = request.state
        question_number = state.get('question_number', 0)
        correct_answers = state.get('correct_answers', 0)

        if intents.AGAIN in request.intents:
            question_number, correct_answers = 0, 0
        elif intents.REPEAT in request.intents:
            question_number = state.get('question_number', 1) - 1
            correct_answers = state.get('correct_answers', 1) - 1
        
        if request.state.get('subject', 2) == 2:
            return self.make_response("Экзамен закончился.", buttons = [button('Что ты умеешь?', hide=True), button('Помощь', hide=True)])

        subject_name = get_name_of_subject(request.state['subject'])
        summary_questions = get_number_of_questions(subject_name)
        if question_number == 0:
            text = 'Класс, давайте начнем! \n'
        else:
            check_answer = state['ques_answer']
            if intents.SKIP in request.intents:
                text = "Правильный ответ: " + ("Да" if check_answer else "Нет") + "\n" + choice(text_config.skip_question) + ". Теперь Вы знаете правильный ответ\n"
            else:
                if check_answer == True or check_answer == False:
                    user_answer = intents.POSITIVE_RESP if (intents.POSITIVE_RESP in request.intents) else intents.NEGATIVE_RESP
                    if (user_answer == intents.POSITIVE_RESP and check_answer == True) or (user_answer == intents.NEGATIVE_RESP and check_answer == False):
                        text = choice(text_config.correct_answer_text) + "!\n"
                        correct_answers += 1
                    else:
                        text = choice(text_config.wrong_answer_text) + "\n"
                else:
                    request_text = request.request_body['request']['original_utterance']
                    if request_text == check_answer:
                        text = choice(text_config.correct_answer_text) + "!\n"
                        correct_answers += 1
                    else:
                        text = choice(text_config.wrong_answer_text) + "\n"

        if question_number == summary_questions:
            if correct_answers <= summary_questions//2:
                text_variant = text_config.less_than_half + "Вам следует повторить материал. \
                А сделать это можно с помощью моих конспектов. Только скажите: «Пришли конспект»."
            elif correct_answers == summary_questions:
                text_variant = text_config.all_right 
            else:
                text_variant = text_config.greater_than_half + "Вам следует повторить материал. \
                А сделать это можно с помощью моих конспектов. Только скажите: «Пришли конспект»."
            text += f"Вы ответили на все вопросы! Ваш результат - {correct_answers} из {summary_questions} правильных ответов.\n{text_variant}"
            return self.make_response(text, buttons = [button('Пришли конспект', hide=True), button('Что ты умеешь?', hide=True)])
               
        if question_number != 0: text += choice(text_config.next_question) + ": \n" 
        question, ques_answer, multiple_answers = get_question(subject_name, question_number + 1)
        
        state['question_number'] = question_number + 1
        answer_options = []
        if multiple_answers:
            text += question + '\n'
            for answer in ques_answer:
                answer_options.append(button(answer['text']))
                if answer['correct']:
                    state['ques_answer'] = answer['text']
        else:
            answer_options = [button("Да"), button("Нет")]
            state['ques_answer'] = ques_answer
            text += question + '\n' + choice(text_config.do_you_agree)
        answer_options.append(button("Пропуск"))
        answer_options.append(button("Начать заново", hide=True))
        answer_options.append(button("Закончить досрочно", hide=True))
        
        state['correct_answers'] = correct_answers
        state['summary_questions'] = summary_questions
        state['scene'] = self.id()
        return self.make_response(text, buttons=answer_options, state=state)
    
    def handle_local_intents(self, request: Request):
        if (intents.POSITIVE_RESP in request.intents or intents.NEGATIVE_RESP in request.intents or intents.SKIP in request.intents or intents.AGAIN in request.intents) and request.state.get('subject', 2) != 2:
            return Exam()
        elif intents.STOP_SESSION in request.intents:
            return NoExam()
        
        if request.state.get('ques_answer', 2) != 2:
            return Exam() 
        
    def fallback(self, request: Request):
        buttons = [button('Что ты умеешь?', hide=True), button('Помощь', hide=True)]
        return self.make_response("Извините, не очень Вас понял", state=request.state, buttons=buttons)

class AskTheme(WithoutDopsaScene):
    def reply(self, request: Request):
        text = 'По какой теме? \nСписок тем: \n'
        
        state = request.state
        state['choose'] = intents.NOTES
        if not intents.REPEAT in request.intents:
            intent = intents.SUBJECT if intents.SUBJECT in request.intents else intents.NOTES_WITH_SUBJECT
            state['subject'] = request.intents[intent]['slots']['subject']['value']
        state['scene'] = self.id()

        themes_list = '\n'.join("- " + el for el in get_themes_of_subject(get_name_of_subject(state['subject']))[:10])
        text += themes_list

        return self.make_response(text, state=state)
    
    def handle_local_intents(self, request: Request):
        text = request.request_body['request']['original_utterance'].lower()
        subject_name = get_name_of_subject(request.state['subject'])
        if subject_name:
            probable_topic = get_link_from_topic_list(name_of_summary=subject_name,
                                                name_of_topic=text)
        if len(probable_topic) != 0:
            return SendNotes()
    
    def fallback(self, request: Request):
        buttons = [button('Что ты умеешь?', hide=True), button('Помощь', hide=True)]
        themes_list = '\n'.join("- " + el for el in get_themes_of_subject(get_name_of_subject(request.state['subject']))[:10])
        return self.make_response(f'Не очень Вас понял. Выберите, пожалуйста, тему \
                                  из следующего списка: \n {themes_list} \n Что выбираете?', tts = "Не очень Вас понял. Выберите, пожалуста, тему \
                                  из следующего списка. Что выбираете?", buttons=buttons, state=request.state)


class AskSubject(WithoutDopsaScene):
    def reply(self, request: Request):
        text = 'По какой дисциплине? \nСписок дисциплин: \n'
        state = request.state
        if intents.NOTES in request.intents:
            state['choose'] = intents.NOTES
        elif intents.EXAM in request.intents:
            state['choose'] = intents.EXAM
        elif intents.TICKET in request.intents:
            state['choose'] = intents.TICKET
        state['scene'] = self.id()

        subject_list_text = '\n'.join("- " + el for el in subject_list)
        text += subject_list_text

        return self.make_response(text, state=state)
    
    def handle_local_intents(self, request: Request):
        if intents.SUBJECT in request.intents and request.state['choose'] == intents.NOTES:
            return AskTheme()
        elif intents.SUBJECT in request.intents and request.state['choose'] == intents.EXAM:
            return StartExam()
        elif intents.SUBJECT in request.intents and request.state['choose'] == intents.TICKET:
            return SendTickets()
    
    def fallback(self, request: Request):
        buttons = [button('Что ты умеешь?', hide=True), button('Помощь', hide=True)]
        subject_list_text = '\n'.join("- " + el for el in subject_list)
        return self.make_response(f'Не очень Вас понял. Выберите, пожалуйста, дисциплину/предмет \
                                  из следующего списка: \n {subject_list_text} \n Что выбираете?', \
                                    tts = "Не очень Вас понял. Выберите, пожалуста, предмет \
                                  из следующего списка. Что выбираете?", buttons=buttons, state=request.state)


class AskGroup(WithoutDopsaScene):
    def reply(self, request: Request):
        text = 'Какой группы? \nСписок групп: \n'
        state = request.state
        state['choose'] = 'schedule'
        state['scene'] = self.id()

        group_list = '\n'.join("- " + el for el in get_groups())
        text += group_list

        buttons = []
        for group in get_groups():
            buttons.append(button(group,hide=True))

        return self.make_response(text, buttons=buttons, state=state)
    
    def handle_local_intents(self, request: Request):
        text = request.request_body['request']['original_utterance']
        groups = get_groups()
        if text in groups:
            return SendSchedule()
    
    def fallback(self, request: Request):
        buttons = []
        for group in get_groups():
            buttons.append(button(group,hide=True))
        group_list = '\n'.join("- " + el for el in get_groups())
        return self.make_response(f'Не очень Вас понял. Выберите, пожалуйста, группу \
                                  из следующего списка: \n {group_list} \n Что выбираете?', \
                                    tts = "Не очень Вас понял. Выберите, пожалуста, группу \
                                  из следующего списка. Что выбираете?", buttons=buttons, state=request.state)
    
class SendSchedule(WithoutDopsaScene):
    def reply(self, request: Request):
        state = request.state
        request_text = request.request_body['request']['original_utterance']


        groups = get_group_name(request_text)
        groups_exist = get_groups()
        for group in groups:
            if group in groups_exist:
                request_text = group
    
        if intents.REPEAT in request.intents:
            request_text = state['group']

        exams_list = get_exams(request_text)
        text = "Расписание экзаменов: \n"
        for i in range(len(exams_list)):
            text += str(i+1) + '. Предмет: ' + exams_list[i]['nameExam'] + ' \nКогда: ' + exams_list[i]['date'] + ' в ' + exams_list[i]['time'] + '\nГде: ' + exams_list[i]['location'] + '\n'
        
        state['group'] = request_text
        state['scene'] = self.id()

        return self.make_response(text, state=state, buttons=[button("Что ты умеешь?", hide=True)])
    
    def handle_local_intents(self, request: Request):
        pass
    
    

class SendTickets(WithoutDopsaScene):
    def reply(self, request: Request):
        state = request.state
        tts = None
        was_tickets = state.get("was_tickets", [])
        if intents.AGAIN in request.intents:
            was_tickets = []

        if len(was_tickets) == 0 and not state.get("ticket_number", False):
            if intents.SUBJECT in request.intents or intents.TICKET_WITH_SUBJECT in request.intents:
                intent = intents.SUBJECT if intents.SUBJECT in request.intents else intents.TICKET_WITH_SUBJECT
                state['subject'] = request.intents[intent]['slots']['subject']['value']
            text = "Правила такие: \nВыбирается случайный билет, если Вы на него не отвечаете, то он остаётся в пуле билетов и может выпасть Вам потом. \
                Иначе билет является засчитанным. Если ответили правильно нажимаете ДА, иначе НЕТ. Поехали - первый билет: \n"
            tts = "Поехали - первый билет"
        elif len(was_tickets) == 12:
            return self.make_response("Ура, билеты закончились!", buttons=[button("Что ты умеешь?", hide=True)])
        else:
            text = "Следующий билет: \n"
            if intents.POSITIVE_RESP in request.intents:
                was_tickets.append(state['ticket_number'])
        
        ticket_number = randint(1,13)
        while ticket_number in was_tickets:
            ticket_number = randint(1, 13)
        
        text += get_ticket(get_name_of_subject(state['subject']), ticket_number)

        state['was_tickets'] = was_tickets
        state['ticket_number'] = ticket_number
        state['scene'] = self.id()

        return self.make_response(text, tts=tts, buttons=[button("Да"), button("Нет")], state=state)

        

    def handle_local_intents(self, request: Request):
        if intents.POSITIVE_RESP in request.intents or intents.NEGATIVE_RESP in request.intents or intents.SKIP in request.intents or intents.AGAIN in request.intents:
            return SendTickets()
        elif intents.STOP_SESSION in request.intents:
            return NoTickets()
        
class NoTickets(WithoutDopsaScene):
    def reply(self, request: Request):
        text = 'Хорошо, перестаю отправлять билеты.'
        buttons = [button('Что ты умеешь?', hide=True), button('Помощь', hide=True)]
        return self.make_response(text, buttons=buttons)
    
    def handle_local_intents(self, request: Request):
        pass


class SendNotes(WithoutDopsaScene):
    def reply(self, request: Request):
        text = request.request_body['request']['original_utterance'].lower()
        probable_topic = get_link_from_topic_list(name_of_summary=get_name_of_subject(request.state['subject']),
                                                name_of_topic=text)
        state = request.state
        state['scene'] = self.id()
        to_say = choice(text_config.send_notes_text) + " К сожалению, без устройства с экраном Вы не увидите конспект."
        return self.make_response(to_say + '\n' + probable_topic[0][1], state=state, \
                                  tts = to_say, buttons=[button("Открыть конспект", url=probable_topic[0][1], hide=True), button("Отправь другой конспект", hide=True)])
    
    def handle_local_intents(self, request: Request):
        pass

    def fallback(self, request: Request):
        buttons = [button('Что ты умеешь?', hide=True), button('Помощь', hide=True)]
        return self.make_response("Это ссылка на материал по вашей теме, перейдя по ней и внимательно прочитав, \
                                  Вы точно будете блистать на экзамене!", buttons=buttons, state = request.state)

class Welcome(WithoutDopsaScene):
    def reply(self, request: Request):
        global database

        text = 'Привет, я твой персональный помощник в сдаче экзаменов! Читай конспекты, проверяй свои знания на экзамене, узнай где и когда поймать препода, \
                попроси меня отправить случайный билет или получи расписание экзаменов своей группы. А если ты вдруг запутался просто скажи "Помощь"'
        buttons = [button('Пришли конспект'), button('Отправь билет'), button('Начни экзамен'), button('Найти препода'), button('Отправь расписание экзаменов'), button('Что ты умеешь?'), button('Помощь'),]
        card = {
            "type": "BigImage",
            "image_id": '1030494/6abdde4afedb5197f950',
            "title": 'Без допсы',
            "description": 'Привет, я твой персональный помощник в сдаче экзаменов! Читай конспекты, проверяй свои знания на экзамене, узнай где и когда поймать препода, \
                попроси меня отправить случайный билет или получи расписание экзаменов своей группы. А если ты вдруг запутался просто скажи "Помощь".',
        }
        try:
            database.insert(request.request_body['session']['user_id'], "hello")
        except:
            pass

        return self.make_response(text, buttons=buttons, card=card)
    
    def handle_local_intents(self, request: Request):
        pass

    def fallback(self, request: Request):
        return self.make_response('Извините, я вас не понял. Я могу прислать конспект, отправить случайный билет, провести викторину по выбранной Вами теме, найти расписание ваших экзаменов или \
                                  показать когда и где поймать препода. Для этого напишите "пришли конспект", "отправь билет", "начни экзамен", "отправь расписание" или "Найти препода"')


def _list_scenes():
    current_module = sys.modules[__name__]
    scenes = []
    for name, obj in inspect.getmembers(current_module):
        if inspect.isclass(obj) and issubclass(obj, Scene):
            scenes.append(obj)
    return scenes


SCENES = {
    scene.id(): scene for scene in _list_scenes()
}

DEFAULT_SCENE = Welcome