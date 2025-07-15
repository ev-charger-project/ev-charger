python3.10 -m venv venv
call venv\Scripts\activate.bat
py -m pip install --upgrade pip
pip install poetry
poetry install
uvicorn app.main:app --reload --port 8000
