import datetime
import json
import os
import requests
import platform


def modification_date(filename):
    t = os.path.getmtime(filename)
    return str(datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%dT%H:%M")) if platform.system() == 'Linux' else \
        str(datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%dT%H.%M"))


start_time = datetime.datetime.now()
try:
    responce = requests.get('https://json.medrating.org/todos')
    todos_json = (json.loads(responce.content))
    responce = requests.get('https://json.medrating.org/users')
    users_json = (json.loads(responce.content))
except requests.exceptions.RequestException as e:
    raise SystemExit(e)
if not os.path.exists('tasks'):
    try:
        os.mkdir('tasks')
    except OSError as e:
        raise SystemExit(e)
for user in users_json:
    userfile_path = "tasks/%s.txt" % user['username']
    if os.path.exists(userfile_path):
        new_userfile_path = "tasks/old_%s_%s.txt" % (user['username'], modification_date(userfile_path))
        try:
            os.rename(userfile_path, new_userfile_path)
        except OSError as e:
            continue
    try:
        userfile = open(userfile_path, "w")
    except IOError:
        print("Невозможно создать файл:", userfile_path)
        continue
    completed_tasks = []
    uncompleted_tasks = []
    for todo_json in todos_json:
        try:
            if todo_json['userId'] == user['id']:
                title = todo_json['title'] if len(todo_json['title']) <= 48 else todo_json['title'][:48]+"..."
                completed_tasks.append(title) if todo_json['completed'] else uncompleted_tasks.append(title)
        except KeyError:
            print("Нет данных для задачи:", todo_json['id'])
        else:
            continue
    try:
        userfile.write("Отчёт для %s.\n%s <%s> %s\nВсего задач: %d\n\nЗавершённые задачи (%d):\n"
                       % (user['company']['name'], user['name'], user['email'],
                          str(datetime.datetime.now().strftime("%d.%m.%Y %H:%M")),
                          len(completed_tasks) + len(uncompleted_tasks), len(completed_tasks)))
        userfile.write("\n".join(map(str, completed_tasks)))
        userfile.write("\n\nОставшиеся задачи (%d):\n" % len(uncompleted_tasks))
        userfile.write("\n".join(map(str, uncompleted_tasks)))
    except IOError:
        print("Невозможно произвести запись в файл:", userfile_path)
        os.remove(userfile_path)
        continue
    except KeyError:
        print("Неврные данные для пользователя", user['id'])
        os.remove(userfile_path)
        continue
    userfile.close()
print('Скрипт выполнился за:', datetime.datetime.now() - start_time)
