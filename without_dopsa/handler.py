from states import STATE_REQUEST_KEY
from scenes import SCENES, DEFAULT_SCENE
from request import Request



def handler(event, context):
    request = Request(event)
    current_scene_id = event.get('state', {}).get(STATE_REQUEST_KEY, {}).get('scene')
    if current_scene_id is None:
        return DEFAULT_SCENE().reply(request)
    current_scene = SCENES.get(current_scene_id, DEFAULT_SCENE)()
    try:
        next_scene = current_scene.move(request)
    except:
        return current_scene.fallback(request)
    if next_scene is not None:
        print(f'Moving from scene {current_scene.id()} to {next_scene.id()}')
        return next_scene.reply(request)
    else:
        print(f'Failed to parse user request at scene {current_scene.id()}')
        return current_scene.fallback(request)
