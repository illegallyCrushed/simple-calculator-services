FROM simple-calculator-base


COPY . .


CMD [ "celery", "-A", "tasks", "worker", "--loglevel=INFO" ]
