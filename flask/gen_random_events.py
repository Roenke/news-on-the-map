#!/usr/bin/python3
from random import random
from datetime import datetime
from app import db, models
from sys import argv

lu = (60.103594, 29.730448)
rb = (59.808320, 30.589201)

count = 100
if len(argv) > 1:
    count = int(argv[1])

for i in range(count):
    e = models.Events(
        title="Event #{}".format(i),
        description="Randomly generated event number {}".format(i),
        date=datetime.utcnow(),
        lat=rb[0] + (lu[0]-rb[0])*random(),
        lng=lu[1] + (rb[1]-lu[1])*random()
    )
    db.session.add(e)

db.session.commit()
