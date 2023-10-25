FROM python:3.10

# WORKDIR /app

# COPY requirements.txt /app/

# RUN pip install --no-cache-dir -r requirements.txt

# COPY CommentSchema.avsc /app/
# COPY SubmissionSchema.avsc /app/
# COPY comment_submission_producer.py /app/
# COPY praw.ini /app/

# CMD ["python", "comment_submission_producer.py"]

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["python","src/comment_submission_producer.py"]