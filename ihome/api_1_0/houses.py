from . import api
from ihome.models import Areas


@api.route('/areas')
def get_areas():
    return 'area page'