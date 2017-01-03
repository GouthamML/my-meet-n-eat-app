# coding=utf-8
import random, string
from app import app
app.config['SECRET_KEY'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
app.run(host='0.0.0.0', port=8000)

