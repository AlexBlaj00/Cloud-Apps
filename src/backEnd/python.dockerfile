FROM python

WORKDIR /backEnd

COPY . /backEnd

COPY requirements.txt .

RUN pip3 install -r requirements.txt

EXPOSE 5000


ENTRYPOINT [ "python3" ]
CMD ["adminNew.py"]