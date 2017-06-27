from cloudshell.delphix.operations.base import BaseOperation


class RestoreVBDOperation(BaseOperation):
    def run(self, vdb_name, group_name, timestamp):
        """Restore given Virtual DB from the timestamp

        :param str vdb_name: virtual DB name
        :param str group_name: group where Virtual DB is located
        :param timestamp:
        :return:
        """
        client = self.get_delphix_client()
        client.refresh_vdb(name=vdb_name, group_name=group_name, timestamp=timestamp)
