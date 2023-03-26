from state import *

def make_response(text, tts=None, state=None, buttons=None):
    response = {
        'text': text,
        'tts': tts if tts is not None else text,
        'end_session': False,
    }
    webhook_response = {
        'response': response,
        'version': '1.0', 
    }
    if state is not None:
        webhook_response[STATE_RESPONSE_KEY] = state
    if buttons is not None:
        response['buttons'] = buttons
    return webhook_response


def button(title, payload=None, url=None, hide=False):
    button = {
        'title': title,
        'hide': hide,
    }
    if payload is not None: button['payload'] = payload
    if url is not None: button['url'] = url
    return button

def welcome_message(event, state):
    text = 'Привет, я твой персональный помощник в сдаче экзаменов! Прочитать конспект или ответить на вопросы?'
    buttons = [button('Что ты умеешь?'), button('Помощь')]
    return make_response(text, state=state, buttons=buttons)

def ask_theme(event, state):
    text = 'На какую тему?'
    return make_response(text, state=state)

def send_notes(event, state):
    text = 'Отправляю конспект на тему ' + state['theme']
    return make_response(text, state=state)

def send_questions(event, state):
    text = 'Отправляю вопросы на тему ' + state['theme']
    return make_response(text, state=state)

def fallback(event, state):
    text = 'Извините, я не поняла'
    return make_response(text, state=state)

def i_can_do(event, state):
    text = 'Я могу прислать конспект или запустить экзамен по нужной Вам теме. Что выбираете?'
    return make_response(text, state=state)

def handler(event, context):
    """
    Entry-point for Serverless Function.
    :param event: request payload.
    :param context: information about current execution context.
    :return: response to be serialized as JSON.
    """
    
    state = event.get('state').get(STATE_REQUEST_KEY, {})
    if event['session']['new']:
        state['screen'] = 'welcome'
        return welcome_message(event, state=state)
    elif 'request' in event and 'original_utterance' in event['request'] \
            and len(event['request']['original_utterance']) > 0:
        text = event['request']['original_utterance'].lower()
        themes = ['матан', 'электротехника', 'программирование']
        if 'конспект' in text: 
            state['choose'] = 'notes'
            return ask_theme(event, state)
        elif 'вопросы' in text: 
            state['choose'] = 'questions'
            state['screen'] = 'choosing theme'
            return ask_theme(event, state)
        for theme in themes:
            if theme in text:
                state['theme'] = theme
                if state['choose'] == 'notes':
                    return send_notes(event, state)
                else:
                    return send_questions(event, state)

        if state['screen'] == 'welcome' or text == 'Что ты умеешь?':
            return i_can_do(event, state)
        return fallback(event, state)

