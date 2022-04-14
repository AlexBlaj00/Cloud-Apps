FROM python

WORKDIR /reporting

COPY . /reporting

COPY requirements.txt .

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

EXPOSE 5003

ENTRYPOINT [ "python3" ]
CMD ["dashboard.py"]