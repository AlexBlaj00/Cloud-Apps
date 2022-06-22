FROM python

WORKDIR /backEnd

COPY . /backEnd

RUN ls

#COPY ./backEnd/requirements.txt .

#RUN pip3 install --upgrade pip

#RUN pip3 install -r requirements.txt

EXPOSE 5000

ENTRYPOINT [ "python3" ]
CMD ["backendServices.py"]