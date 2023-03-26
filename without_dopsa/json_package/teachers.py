import requests
from bs4 import BeautifulSoup
from json_package.json_tool import write_to_json, load_from_json


def found_teachers_link(prepod: str):
    prepod = prepod.title()
    url = f'https://itmo.ru/ru/schedule/1/{prepod}/schedule.htm'
    response = requests.get(url)
    html = response.content

    soup = BeautifulSoup(html, 'html.parser')

    res = soup.find("article", class_="content_block")
    link_list = res.find_all('a')

    for link in link_list:
        if prepod in link.text:
            name = ' '.join(link.text.split()[:3]) 
            return link, name

    return False, False
        

def parse_teacher_schedule(link: str):
    response = requests.get('https://itmo.ru/' + link)
    html = response.content

    soup = BeautifulSoup(html, 'html.parser')

    days_lesson = {}
    for th in soup.find_all('th', {'class': 'day'}):
        day = th.text.strip()
        if not day:
            day = last_day
        data = days_lesson.get(day, [])

        schedule = {}
        td_time = th.find_next_sibling('td', {'class': 'time'})
        if not td_time: continue
        schedule['time'] = td_time.text.strip().split()[0]

        td_room = th.find_next_sibling('td', {'class': 'room'})
        if not td_room: continue
        schedule['room'] = ' '.join(td_room.text.strip().split())
        
        if len(data) == 0 or data[-1] != schedule: 
            data.append(schedule)
            days_lesson[day] = data
        last_day = day

    return days_lesson
    

def get_teacher_schedule(name: str):
    teachers = load_from_json("json_package/teachers.json")
    for teacher in teachers:
        if teacher['name'] == name:
            return teacher['schedule']

    link, actual_name = found_teachers_link(name)
    schedule = parse_teacher_schedule(link['href'])
    teacher_and_schedule = {
        'name': actual_name,
        'schedule': schedule
    }
    teachers.append(teacher_and_schedule)
    # write_to_json("json_package/teachers.json", teachers)
    return schedule



if __name__ == "__main__":
    print(get_teacher_schedule('хованцева'))
    