from cloudshell.delphix.operations.base import BaseOperation


class RefreshVBDOperation(BaseOperation):
    def run(self, vdb_name, group_name):
        """Refresh given Virtual DB

        :param str vdb_name: virtual DB name
        :param str group_name: group where Virtual DB is located
        :return:
        """
        client = self.get_delphix_client()
        client.refresh_vdb(name=vdb_name, group_name=group_name)
