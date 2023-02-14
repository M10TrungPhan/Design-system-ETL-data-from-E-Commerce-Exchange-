from apis.routes.base_route import BaseRoute

from services.manage_keyword_service import ManageKeyWord


class ManualRoute(BaseRoute):
    def __init__(self):
        super(ManualRoute, self).__init__(prefix="")
