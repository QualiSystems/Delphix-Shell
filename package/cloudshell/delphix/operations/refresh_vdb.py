from cloudshell.delphix.operations.base import BaseOperation


class RefreshVBDOperation(BaseOperation):

    def run(self, vdb_name, group_name):
        client = self.get_delphix_client()
        client.refresh_vdb(name=vdb_name, group_name=group_name)
