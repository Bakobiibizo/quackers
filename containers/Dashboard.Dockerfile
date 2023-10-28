FROM ubuntu:22.04

WORKDIR /app
RUN apt update && apt upgrade -y
RUN apt install build-essential -y
RUN apt install python3 python3-pip -y
RUN python3 -m pip install --upgrade pip
RUN pip install setuptools wheel
RUN apt install python-is-python3
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY src /app

EXPOSE 8501

CMD streamlit run dashboard/dashboard.py
