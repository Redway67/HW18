from flask import Flask, render_template, request
from modules.parser import parser, get_history, get_request

Info = {}

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/result/', methods=['GET'])
@app.route('/history/', methods=['GET'])
def history():
    history_db = get_history()
    return render_template('history.html', req=history_db)


@app.route('/history/', methods=['POST'])
def history_result():
    v_request = request.form.get('request')
    if v_request:
        global Info
        Info = get_request(v_request)
        return render_template('result.html', info=Info)
    # не выбран запрос!!
    history_db = get_history()
    return render_template('history.html', req=history_db)


@app.route('/search/', methods=['GET'])
def search():
    return render_template('search.html')


@app.route('/search/', methods=['POST'])
def get_search():
    global Info
    Info = parser(request.form['vacancy'], request.form['region'])
    return render_template('result.html', info=Info)


@app.route('/result/', methods=['POST'])
def results():
    global Info
    if Info:
        return render_template('result.html', info=Info)
    history_db = get_history()
    return render_template('history.html', req=history_db)


@app.route('/contacts/')
def contacts():
    return render_template('contacts.html')


if __name__ == '__main__':
    app.run(debug=True)
