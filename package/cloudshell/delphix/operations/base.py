from cloudshell.delphix.delphix_client import DelphixClient


class BaseOperation(object):

    def __init__(self, engine_conf, logger):
        self._engine_conf = engine_conf
        self._logger = logger

    def get_delphix_client(self):
        return DelphixClient(engine_conf=self._engine_conf)
