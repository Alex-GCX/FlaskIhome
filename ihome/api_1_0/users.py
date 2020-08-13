from . import api


@api.route('/user')
def user():
    return 'user page'
