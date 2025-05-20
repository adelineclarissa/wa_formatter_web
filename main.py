from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import re
from datetime import datetime
import os
import shutil

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def parse_chat_line(line):
    match = re.match(
        r"(\d{1,2}/\d{1,2}/\d{2}),\s(\d{1,2}:\d{2})\s?(AM|PM)?\s-\s([^:]+):\s(.+)", line
    )
    if match:
        date_str, time_str, am_pm, display_name, message = match.groups()
        full_time_str = f"{time_str} {am_pm}" if am_pm else time_str
        dt = datetime.strptime(f"{date_str} {full_time_str}", "%m/%d/%y %I:%M %p")

        if display_name == "Rahasia Ketenangan Hati":
            display_name = "IDI"

        return {
            "date": dt.date().isoformat(),
            "time": dt.time().strftime("%H:%M"),
            "display_name": display_name.strip(),
            "message": message.strip(),
        }
    return None


def ensure_unique_minute(chat, used_times):
    hh, mm = map(int, chat["time"].split(":"))
    while True:
        time_candidate = f"{str(hh).zfill(2)}:{str(mm).zfill(2)}"
        if time_candidate not in used_times:
            used_times.add(time_candidate)
            chat["time"] = time_candidate
            return chat
        mm += 1
        if mm >= 60:
            mm = 0
            hh = (hh + 1) % 24


def print_chat(chat):
    time_12h = datetime.strptime(chat["time"], "%H:%M").strftime("%I:%M %p")
    formatted_date = datetime.strptime(chat["date"], "%Y-%m-%d").strftime("%m/%d/%Y")
    return f"[{time_12h}, {formatted_date}] {chat['display_name']}:{chat['message']}"


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_file(file: UploadFile):
    contents = await file.read()
    lines = contents.decode("utf-8").splitlines()
    used_times_by_date = {}
    chat_output = []

    for line in lines:
        chat = parse_chat_line(line)
        if chat:
            date = chat["date"]
            if date not in used_times_by_date:
                used_times_by_date[date] = set()
            chat = ensure_unique_minute(chat, used_times_by_date[date])
            chat_output.append(chat)

    output_file = f"{file.filename.replace('.txt', '')}_formatted.txt"
    output_path = os.path.join("static", output_file)

    with open(output_path, "w", encoding="utf-8") as f:
        for chat in chat_output:
            f.write(print_chat(chat) + "\n")

    return {"filename": output_file}
