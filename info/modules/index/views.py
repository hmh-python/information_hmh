from . import index_blue

@index_blue.route('/')
def index():

    return ('hello word(blue)')