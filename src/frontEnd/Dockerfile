FROM python

WORKDIR /frontEnd

COPY  . /frontEnd

COPY requirements.txt .

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

EXPOSE 4000

ENTRYPOINT [ "python3" ]
CMD ["main.py"]

