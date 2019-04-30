from utils import generate_alarm

# create a flask application - this ``app`` object will be used to handle
# inbound requests, routing them to the proper 'view' functions, etc
app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/', methods=['POST'])
def result:
    generate_alarm(1);

    return "Done!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
