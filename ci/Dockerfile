FROM python:3.7
COPY ./*.py /
RUN pip install --upgrade flask pandas flask_cors matplotlib seaborn pymongo statsmodels
CMD ["python3", "-u", "main_user.py"]
