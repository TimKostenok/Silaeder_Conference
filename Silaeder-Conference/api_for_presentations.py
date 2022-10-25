from fastapi import FastAPI
import sqlite3
app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def remake_data(projects, cur):
    result = projects
    for i in range(len(result)):
        result[i] = {'id': result[i][0], 'name': result[i][1], 'autors': result[i][3], 'presentation':{'pdf': result[i][2], 'videos': []}}
        que = "SELECT video_wishes, video FROM silsite_video WHERE id={}".format(result[i]['id'])
        cur.execute(que)
        videos = cur.fetchall()
        for j in videos:
            result[i]['presentation']['videos'].append({'after_slide': j[0][0], 'YT': j[0][1]})
    return result

@app.get("/projects")
def projects():
    con = sqlite3.connect('db.sqlite3')
    cur = con.cursor()
    que = "SELECT id, name, presentation,students FROM silsite_project"
    cur.execute(que)
    result = cur.fetchall()
    result = remake_data(result, cur)
    cur.close()
    return result

@app.get("/project/{project_id}")
def project(project_id=None):
    con = sqlite3.connect('db.sqlite3')
    cur = con.cursor()
    que = "SELECT id, name, presentation, students FROM silsite_project WHERE id={}".format(project_id)
    cur.execute(que)
    result = cur.fetchall()
    result = remake_data(result, cur)
    cur.close()
    return result[0]

@app.get("/project")
def project_by_name(q=None):
    con = sqlite3.connect('db.sqlite3')
    cur = con.cursor()
    que = "SELECT id, name, presentation, students FROM silsite_project"
    cur.execute(que)
    result = cur.fetchall()
    result = remake_data(result, cur)
    cur.close()
    sorted_result = []
    for i in result:
        if q.lower() in i['name'].lower():
            sorted_result.append(i)
    return sorted_result
