FROM python

WORKDIR /frontEnd

COPY  . /frontEnd

RUN ls

#COPY ./frontEnd/requirements.txt .

#RUN pip3 install --upgrade pip

#RUN pip3 install -r requirements.txt

EXPOSE 4000

ENTRYPOINT [ "python3" ]
CMD ["main.py"]