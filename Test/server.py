#Server-side script
from flask import Flask, request, g
import numpy as np
import torch
import torch.nn as nn
import time
import os
from data_generator import data
import json
from peewee import *

DATABASE = 'POSCHAIR.db'

app = Flask(__name__)

# create a peewee database instance -- our models will use this database to
# persist information
database = SqliteDatabase(DATABASE)

# model definitions -- the standard "pattern" is to define a base model class
# that specifies which database to use.  then, any subclasses will automatically
# use the correct storage. for more information, see:
# http://charlesleifer.com/docs/peewee/peewee/models.html#model-api-smells-like-django
class BaseModel(Model):
    class Meta:
        database = database
        db_table = 'Posture'

# the user model specifies its fields (or columns) declaratively, like django
class Posture(BaseModel):
    ID = CharField(unique=True)
    value = CharField()
    ultra_value = CharField()
    label = IntegerField()
    date = DateTimeField(default=datetime.datetime.now)


def test_model(model_name, image):
    #=======================================
    # deep learning model test
    # - input: (180*180*3) image
    # - output: posture label(0-15)
    #=======================================
    model = torch.load("../../haeyoon/"+model_name, map_location='cpu')
    model.eval()
    model=model.cpu()

    x = image.astype('float32')/255
    x = x.reshape(1, x.shape[0], x.shape[1], x.shape[2])
    x_ = torch.from_numpy(x.transpose((0,3,1,2)))
    x_ = x_.cpu()

    y_p = model(x_)
    y_p = y_p.detach().numpy()
    return np.argmax(y_p, axis=1)

@app.before_request
def before_request():
    print('before_request')
    g.db = database
    g.db.connect()


@app.after_request
def after_request(response):
    print('close_request')
    g.db.close()
    return response

@app.route('/', methods=['POST'])
def result():
    if request.method=='POST':
        try:
            d = data()

            data_string = request.form['data']
            val = json.loads(data_string) # pressure and ultrasonic value from arduino

            with database.atomic():
                data = Posture.create(
                    ID="choo@naver.com",
                    value=val
                    )

                val = val[:-2]
                image = d.generator(value)
                y = test_model("model0225.pth", image) #model path, image array .. => .. .. ..
                print("label predicted: ",y)
            return "received!"

        except IntegrityError:
            return "inserting error"

    else:
        return "success"

if __name__=='__main__':
 app.run(host='0.0.0.0',port=80,debug=True)

