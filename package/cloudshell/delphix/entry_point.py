from delphixpy.v1_6_0.delphix_engine import DelphixEngine
from delphixpy.v1_6_0 import web


class DelphixShell(object):

    def __init__(self):
        self._vdb_params_prepare_map = {
            "mssql": self._prepare_mssql_vdb_params,
            # "oracle": ...
            # "mysql": ...
            # "postreg": ...
            # "...": ...
        }

    def _get_engine(self):
        # todo: Where to get these HARDCODED VALUES???? <<--- move this to the resource
        address = "192.168.85.31:8888"
        user = "delphix_admin"
        password = "Quali123"
        namespace = "DOMAIN"

        return DelphixEngine(address=address,
                             user=user,
                             password=password,
                             namespace=namespace)


    # def get_inventory(self, context):
        # logger = get_logger_with_thread_id(context)
        # api = get_api(context)
        # logger.info("{}".format(context.resource.attributes))
        # return AutoLoadDetails([], [])

    def _get_repository(self, engine, env, repo_type):
        """

        :param engine:
        :param env:
        :param repo_type:
        :return:
        """
        for repo in web.repository.get_all(engine=engine, environment=env.reference):
            if repo.type == repo_type:
                return repo

        raise Exception("Repo was not found")

    def _find_obj_by_name(self, collection, name):
        """

        :param list collection:
        :param str name:
        :return:
        """
        for obj in collection:
            if obj.name == name:
                return obj

        raise Exception("Object was not found")

    def _prepare_mssql_vdb_params(self, engine, env, group, db_name, source_database):
        """

        :param engine:
        :param env:
        :param group:
        :param db_name:
        :param source_database:
        :return:
        """
        repo_type = "MSSqlInstance"
        vdb_params = web.vo.MSSqlProvisionParameters()
        vdb_params.source = web.vo.MSSqlVirtualSource()
        vdb_params.container = web.vo.MSSqlDatabaseContainer()
        vdb_params.container.group = group.reference
        vdb_params.container.name = db_name

        vdb_params.source_config = web.vo.MSSqlSIConfig()
        vdb_params.source_config.database_name = db_name
        vdb_params.source_config.instance = web.vo.MSSqlInstanceConfig()
        vdb_params.source_config.instance.host = env.host
        timeflow_point_parameters = web.vo.TimeflowPointSemantic()
        timeflow_point_parameters.location = "LATEST_POINT"
        timeflow_point_parameters.container = source_database.reference
        vdb_params.timeflow_point_parameters = timeflow_point_parameters

        repo = self._get_repository(engine=engine, env=env, repo_type=repo_type)
        vdb_params.source_config.repository = repo.reference

        return vdb_params

    def provision_vdb(self, target_db_name, souce_db_name, source_group_name, target_group_name, vdb_type, timestamp, logger):

        host_name = "192.168.65.69"  # ENV to save <-- this needed to be recognized from the reservation !

        # api = get_api(context)
        from cloudshell.api.cloudshell_api import CloudShellAPISession
        from cloudshell.shell.core.context_utils import get_reservation_context_attribute
        reservation_id = get_reservation_context_attribute('reservation_id', context)


        # todo: use api to decrypt password


        # find correct resource???
        # api.GetReservationDetails("992c9402-f2b2-4dfb-a7be-68ca01e9b8c0").ReservationDescription.Resources[0].LogicalResource.__dict__

        # import ipdb;ipdb.set_trace()

        engine = self._get_engine()

        all_groups = web.group.get_all(engine=engine)

        target_group = self._find_obj_by_name(collection=all_groups, name=target_group_name)
        source_group = self._find_obj_by_name(collection=all_groups, name=source_group_name)

        all_dbs = web.database.get_all(engine=engine, group=source_group.reference)
        source_database = self._find_obj_by_name(collection=all_dbs, name=souce_db_name)

        all_envs = web.environment.get_all(engine=engine)
        env = self._find_obj_by_name(collection=all_envs, name=host_name)

        if vdb_type.lower() not in self._vdb_params_prepare_map:
            raise Exception("Unknown VDB type {}. Supported types are {}".format(vdb_type,
                                                                                 self._vdb_params_prepare_map.keys()))

        prepare_vdb_params_handler = self._vdb_params_prepare_map[vdb_type.lower()]

        vdb_params = prepare_vdb_params_handler(engine=engine,
                                                env=env,
                                                group=target_group,
                                                db_name=target_db_name,
                                                source_database=source_database)

        # by default operation is a synchronous
        web.database.provision(engine, vdb_params)

    def delete_vdb(self, vdb_name, group_name, logger):
        # todo: do we need support for group_name == "all" and database_name == "all" ?

        engine = self._get_engine()

        all_groups = web.group.get_all(engine=engine)
        group = self._find_obj_by_name(collection=all_groups, name=group_name)

        all_dbs = web.database.get_all(engine=engine, group=group.reference)
        try:
            db = self._find_obj_by_name(collection=all_dbs, name=vdb_name)
        except Exception: # except not found error
            logger.warning("Already deleted...")
        else:
            # if source_obj.staging == False and source_obj.virtual == True: ??
            web.database.delete(engine=engine, ref=db.reference)

    def refresh_vdb(self, group_name, vdb_name, logger):
        # todo: get all needed variables from context
        engine = self._get_engine()

        all_groups = web.group.get_all(engine=engine)
        source_group = self._find_obj_by_name(collection=all_groups, name=group_name)

        all_dbs = web.database.get_all(engine=engine, group=source_group.reference)
        db = self._find_obj_by_name(collection=all_dbs, name=vdb_name)

        if db.reference.lower().startswith("oracle"):
            refresh_params = web.vo.OracleRefreshParameters()
        else:
            refresh_params = web.vo.RefreshParameters()

        source_db = web.database.get(engine, db.provision_container)
        timeflow_point_parameters = web.vo.TimeflowPointSemantic()
        timeflow_point_parameters.location = "LATEST_POINT"
        timeflow_point_parameters.container = source_db.reference
        refresh_params.timeflow_point_parameters = timeflow_point_parameters

        web.database.refresh(engine=engine, ref=db.reference, refresh_parameters=refresh_params)

    def restore_vdb(self, group_name, vdb_name, time_stamp="latest"):
        # todo: same as refresh but with a timestamp !!
        pass
        # Delphix.VDB.refresh_existing_db_on_target.main(target_environment_name,group_name,vdb_target_name,time_stamp)


# test
shell = DelphixShell()

import logging
logger = logging.getLogger(__name__)

# shell.provision_vdb(target_db_name="testAntTargetNewDB1",
#                     souce_db_name="Quali1",
#                     source_group_name="Default Group",
#                     target_group_name="testAntGroup",
#                     vdb_type="mssql",
#                     timestamp="latest",
#                     logger=logger)

shell.provision_vdb(target_db_name="testAntTargetNewDB1111",
                    souce_db_name="Quali1",
                    source_group_name="Default Group",
                    target_group_name="testAntGroup",
                    vdb_type="mssql",
                    timestamp="latest",
                    logger=logger)


# shell.delete_vdb(vdb_name="testAntTargetNewDB1", group_name="testAntGroup", logger=logger)
# shell.refresh_vdb(vdb_name="testAntTargetNewDB1", group_name="testAntGroup", logger=logger)



