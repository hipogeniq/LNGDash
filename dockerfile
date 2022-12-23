FROM python:3.9

EXPOSE 8505

WORKDIR /app

# Upgrade pip and install requirements
COPY requirements.txt requirements.txt
RUN pip install -U pip
RUN pip install -r requirements.txt

# Copy app code and set working directory
COPY . .
WORKDIR /app

ENTRYPOINT ["streamlit", "run", "streamlit_app_simplified.py", "--server.port=8505", "--server.address=0.0.0.0"]



