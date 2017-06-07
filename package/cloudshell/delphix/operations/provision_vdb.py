from cloudshell.delphix.operations.base import BaseOperation


class ProvisionVBDOperation(BaseOperation):

    def _get_delphix_target_resource(self, cloudshell_api, reservation_id):
        cs_resources = cloudshell_api.GetReservationDetails(reservation_id).ReservationDescription.Resources

        if len(cs_resources) == 1:
            raise Exception("Reservation doesn't contain Delphix Target resource")
        elif len(cs_resources) > 2:
            raise Exception("Reservation contains additional resources")

        for resource in cs_resources:
            if resource.ResourceModelName == "Generic App Model":  # cloned VM will be generic model
                return cloudshell_api.GetResourceDetails(resource.Name)

        raise Exception("Unable to find Delphix Target resource on the CloudShell")

    def run(self, target_db_name, souce_db_name, source_group_name, target_group_name, timestamp, vdb_type,
            cloudshell_api, reservation_id):
        """

        :param target_db_name:
        :param souce_db_name:
        :param source_group_name:
        :param target_group_name:
        :param timestamp:
        :param vdb_type:
        :param cloudshell_api:
        :return:
        """
        client = self.get_delphix_client()
        target_group = client.get_group(name=target_group_name)

        target_resource = self._get_delphix_target_resource(cloudshell_api=cloudshell_api,
                                                            reservation_id=reservation_id)


        # todo: check if we need to use Public IP attribute or can just get the resource address
        client.create_windows_target_env(target_resource.Address, )

        # env = client.get_env_by_ip(address=target_resource.Address, user, password, env_name=target_resource.Name)

        # todo: change password type from the string to some secret one on the cloudshell model + decrypt it before usage in parser !!!
        # todo: install target env on the prepare connectivity step !!!


        # todo: use api to decrypt password

        # from cloudshell.api.cloudshell_api import CloudShellAPISession
        # api = CloudShellAPISession(host="192.168.85.13",
        #                            token_id="",
        #                            username="admin",
        #                            password="admin",
        #                            domain="Global")

        # source_database = client.get_database(name=souce_db_name, group_name=source_group_name)
        # client.provision_vdb(env=env,
        #                      group=target_group,
        #                      db_name=target_db_name,
        #                      source_database=source_database,
        #                      vdb_type=vdb_type)
