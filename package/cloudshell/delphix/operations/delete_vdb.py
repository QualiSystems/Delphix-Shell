from cloudshell.delphix.exceptions import NotFoundResourceException
from cloudshell.delphix.operations.base import BaseOperation


class DeleteVBDOperation(BaseOperation):
    def run(self, vdb_name, group_name):
        """Delete given Virtual DB from the Delphix

        :param str vdb_name: virtual DB name
        :param str group_name: group where Virtual DB is located
        :return:
        """
        client = self.get_delphix_client()
        try:
            vdb = client.get_database(name=vdb_name, group_name=group_name)
        except NotFoundResourceException:
            self._logger.warning("VDB {} was already deleted".format(vdb_name))
        else:
            client.delete_database(reference=vdb.reference)
