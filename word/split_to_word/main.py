from flask import Flask, request
from janome.tokenizer import Tokenizer
import json

app = Flask(__name__)


@app.route("/", methods=['GET'])
def split_to_word():
    message = request_message()
    words = get_token(message)
    header = get_header()

    return (
        json.dumps(dict(words=words), indent=2, ensure_ascii=False),
        header
    )


def request_message():
    """ 分解対象の文章を取得する
    """
    request_json = request.get_json()
    key = 'message'

    message = ''
    if request.args and key in request.args:
        message = request.args.get(key)
    elif request_json and key in request_json:
        message = request_json[key]

    return message


def get_token(message: str):
    t = Tokenizer()
    words = [word.base_form for word in t.tokenize(message)]
    return words


def get_header():
    headers = {}
    headers['Access-Control-Allow-Origin'] = '*'
    headers['Access-Control-Allow-Headers'] = (
        'Origin, X-Requested-With, Content-Type, Accept'
    )
    return headers


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
