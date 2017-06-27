from cloudshell.shell.core.driver_context import AutoLoadDetails

from cloudshell.delphix.operations.base import BaseOperation


class AutoloadOperation(BaseOperation):
    def run(self):
        """Verify that Delphix engine configuration is correct"""
        self.get_delphix_client()
        return AutoLoadDetails([], [])
