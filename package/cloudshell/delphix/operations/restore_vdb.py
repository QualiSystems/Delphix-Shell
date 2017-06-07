from cloudshell.delphix.operations.base import BaseOperation


class RestoreVBDOperation(BaseOperation):

    def run(self, vdb_name, group_name, timestamp):
        client = self.get_delphix_client()
        client.refresh_vdb(name=vdb_name, group_name=group_name, timestamp=timestamp)
