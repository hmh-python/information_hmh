from info import curren_app

app = curren_app("Develo")

@app.route('/')
def index():

    return ('hello word!')

if __name__ == '__main__':
    app.run()