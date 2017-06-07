from cloudshell.devices import driver_helper
from cloudshell.shell.core.context_utils import get_reservation_context_attribute
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface

from cloudshell.delphix.operations import AutoloadOperation
from cloudshell.delphix.operations import DeleteVBDOperation
from cloudshell.delphix.operations import ProvisionVBDOperation
from cloudshell.delphix.operations import RefreshVBDOperation
from cloudshell.delphix.operations import RestoreVBDOperation
from cloudshell.delphix.parser import parse_delphix_resource


class DelphixDriver(ResourceDriverInterface):

    def cleanup(self):
        pass

    def initialize(self, context):
        pass

    def get_inventory(self, context):
        logger = driver_helper.get_logger_with_thread_id(context)
        engine_config = parse_delphix_resource(context)
        autoload_operation = AutoloadOperation(engine_conf=engine_config,
                                               logger=logger)
        return autoload_operation.run()

    def provision_vdb(self, context, target_db_name, source_db_name, source_group_name, target_group_name, timestamp,
                      vdb_type):
        logger = driver_helper.get_logger_with_thread_id(context)
        engine_config = parse_delphix_resource(context)
        cs_api = driver_helper.get_api(context)
        provision_operation = ProvisionVBDOperation(engine_conf=engine_config,
                                                    logger=logger)

        reservation_id = get_reservation_context_attribute('reservation_id', context)
        provision_operation.run(target_db_name=target_db_name,
                                souce_db_name=source_db_name,
                                source_group_name=source_group_name,
                                target_group_name=target_group_name,
                                timestamp=timestamp,
                                vdb_type=vdb_type,
                                cloudshell_api=cs_api,
                                reservation_id=reservation_id)

    def delete_vdb(self, context, vdb_name, group_name):
        logger = driver_helper.get_logger_with_thread_id(context)
        engine_config = parse_delphix_resource(context)
        delete_operation = DeleteVBDOperation(engine_conf=engine_config,
                                              logger=logger)

        delete_operation.run(vdb_name=vdb_name, group_name=group_name)

    def refresh_vdb(self, context, group_name, vdb_name):
        logger = driver_helper.get_logger_with_thread_id(context)
        engine_config = parse_delphix_resource(context)
        refresh_operation = RefreshVBDOperation(engine_conf=engine_config,
                                                logger=logger)

        refresh_operation.run(vdb_name=vdb_name, group_name=group_name)

    def restore_vdb(self, context, group_name, vdb_name, timestamp):
        logger = driver_helper.get_logger_with_thread_id(context)
        engine_config = parse_delphix_resource(context)
        restore_operation = RestoreVBDOperation(engine_conf=engine_config,
                                                logger=logger)

        restore_operation.run(vdb_name=vdb_name, group_name=group_name, timestamp=timestamp)
