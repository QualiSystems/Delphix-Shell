from cloudshell.shell.core.driver_context import AutoLoadDetails

from cloudshell.delphix.operations.base import BaseOperation


class AutoloadOperation(BaseOperation):

    def run(self):
        self.get_delphix_client()  # verify set Delphix engine configuration is correct
        return AutoLoadDetails([], [])
