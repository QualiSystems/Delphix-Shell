from cloudshell.delphix.operations.base import BaseOperation


class ProvisionVBDOperation(BaseOperation):
    def _get_target_ip_addr(self, cloudshell_api, reservation_id):
        """Get IP Address from the deployed Delphix Target VM

        :param cloudshell_api:
        :param str reservation_id:
        :rtype: str
        """
        cs_resources = cloudshell_api.GetReservationDetails(reservation_id).ReservationDescription.Resources

        if len(cs_resources) == 1:
            raise Exception("Reservation doesn't contain Delphix Target resource")
        elif len(cs_resources) > 2:
            raise Exception("Reservation contains additional resources")

        for resource in cs_resources:
            if resource.ResourceModelName == "Generic App Model":  # cloned VM will be generic model
                target = cloudshell_api.GetResourceDetails(resource.Name)
                return target.Address

        raise Exception("Unable to find Delphix Target resource on the CloudShell")

    def run(self, target_db_name, souce_db_name, source_group_name, target_group_name, timestamp, vdb_type,
            cloudshell_api, reservation_id):
        """Provision vDB in the target group from the given source DDB

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
        source_database = client.get_database(souce_db_name, source_group_name)

        target_group = client.get_group(target_group_name)
        target_ip = self._get_target_ip_addr(cloudshell_api=cloudshell_api, reservation_id=reservation_id)
        env = client.get_env_by_ip(ip_addr=target_ip)

        client.provision_vdb(env=env,
                             group=target_group,
                             db_name=target_db_name,
                             source_database=source_database,
                             vdb_type=vdb_type)
