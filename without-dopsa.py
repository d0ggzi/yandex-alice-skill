STATE_RESPONSE_KEY = 'session_state'
STATE_REQUEST_KEY = 'session'

def make_response(text, tts=None, state=None):
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
    return webhook_response

def welcome_message(event):
    text = 'Привет, я твой персональный помощник в сдаче экзаменов! Прочитать конспект или ответить на вопросы?'
    return make_response(text)

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

def handler(event, context):
    """
    Entry-point for Serverless Function.
    :param event: request payload.
    :param context: information about current execution context.
    :return: response to be serialized as JSON.
    """
    
    if event['session']['new']:
        return welcome_message(event)
    elif 'request' in event and 'original_utterance' in event['request'] \
            and len(event['request']['original_utterance']) > 0:
        state = event.get('state').get(STATE_REQUEST_KEY, {})
        
        text = event['request']['original_utterance']
        themes = ['матан', 'электротехника', 'программирование']
        if 'конспект' in text: 
            state['choose'] = 'notes'
            return ask_theme(event, state)
        elif 'вопросы' in text: 
            state['choose'] = 'questions'
            return ask_theme(event, state)
        for theme in themes:
            if theme in text:
                state['theme'] = theme
                if state['choose'] == 'notes':
                    return send_notes(event, state)
                else:
                    return send_questions(event, state)

        return fallback(event, state)

