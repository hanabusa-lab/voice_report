from flask import Flask, request
from gensim.models.word2vec import Word2Vec
import json

app = Flask(__name__)


def load_model():
    model_name = 'model/word2vec.gensim.model'

    model = Word2Vec.load(model_name)
    return model


model = load_model()


@app.route("/", methods=['POST'])
def split_to_word():
    message = request_message()
    key = request_key()
    header = get_header()

    similarity_list = [
        {
            'word': word,
            'similarity': f'{model.similarity(key, word)}',
        } for word in message
    ]

    return (
        json.dumps(
            dict(key=key, similarity=similarity_list),
            indent=2,
            ensure_ascii=False
        ),
        header
    )


def request_key():
    """ 類似度計算に利用するキー単語を取得する
    """
    request_json = request.get_json()
    key = 'key'

    message = ''
    if request.args and key in request.args:
        message = request.args.get(key)
    elif request_json and key in request_json:
        message = request_json[key]

    return message


def request_message():
    """ 類似度計算する単語リストを取得する
    """
    request_json = request.get_json()
    key = 'message'

    message = ''
    if request.args and key in request.args:
        message = request.args.get(key)
    elif request_json and key in request_json:
        message = request_json[key]

    return message


def get_header():
    headers = {}
    headers['Access-Control-Allow-Origin'] = '*'
    headers['Access-Control-Allow-Headers'] = (
        'Origin, X-Requested-With, Content-Type, Accept'
    )
    return headers


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=20080)
