FROM python:3.9-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./best_paper_short.mp3 /app/best_paper_short.mp3
COPY ./best_paper.mp3 /app/best_paper.mp3
COPY ./best_paper_2.mp3	/app/best_paper_2.mp3
COPY ./welcome.mp3	/app/welcome.mp3
COPY ./streamlit_data.pkl /app/streamlit_data.pkl
COPY ./streamlit_icml_data.pkl /app/streamlit_icml_data.pkl
COPY ./overview_icml.mp3 /app/overview_icml.mp3

COPY ./ui_streamlit.py /app/app.py

EXPOSE 8080

CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
