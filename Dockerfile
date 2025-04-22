FROM python:3.11
LABEL dustychuuu dustychuuu@gmail.com

COPY . .

RUN apt-get update -y \
    && apt-get upgrade pip -y \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

WORKDIR /belfoot_fantasy

RUN cd belfoot_fantasy \
    && echo "import os" > env.py \
    && echo "def set_env():" >> env.py \
    && echo "    os.environ['SECRET_KEY'] = 'django-insecure-+&!)jq^(5f64m+=$yg9c79v_b)wa2=#\$8&16v7e58op_5wwrmb'" >> env.py \
    && echo "    os.environ['NAME'] = 'belfoot_fantasy_1_db'" >> env.py \
    && echo "    os.environ['USER'] = 'postgres'" >> env.py \
    && echo "    os.environ['PASSWORD'] = 'postgres'" >> env.py \
    && echo "    os.environ['HOST'] = 'my_postgres1'" >> env.py \
    && echo "    os.environ['PORT'] = '5432'" >> env.py

CMD python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py runserver 0.0.0.0:8000 
    
