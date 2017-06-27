from delphixpy.v1_6_0.delphix_engine import DelphixEngine
from delphixpy.v1_6_0 import web

from cloudshell.delphix.exceptions import UnsupportedVDBException
from cloudshell.delphix.exceptions import NotFoundResourceException


class DelphixClient(object):

    def __init__(self, engine_conf):
        """

        :param cloudshell.delphix.parser.DelphixEngineConfig engine_conf:
        """
        self._vdb_params_prepare_map = {
            "mssql": self._prepare_mssql_vdb_params
        }
        self._engine = self._get_engine(engine_conf)
        self._cache = {}

    def _get_engine(self, engine_conf):
        """Get Delphix Engine based on given configuration object

        :param cloudshell.delphix.parser.DelphixEngineConfig engine_conf:
        :return:
        """
        return DelphixEngine(address=engine_conf.address,
                             user=engine_conf.user,
                             password=engine_conf.password,
                             namespace=engine_conf.namespace)

    def _get_all_resources(self, resource_cls):
        """Get all resources from the Delphix

        :param resource_cls:
        :rtype: list[delphixpy.v1_6_0.web.vo.NamedUserObject]
        """
        if resource_cls not in self._cache:
            self._cache[resource_cls] = resource_cls.get_all(engine=self._engine)

        return self._cache[resource_cls]

    def get_group(self, name):
        """Get Delphix group by its name

        :param str name: group name
        :rtype: delphixpy.v1_6_0.web.vo.Group
        """
        resources = self._get_all_resources(web.group)
        return self._find_resource_by_attr(collection=resources, attr_value=name)

    def get_env(self, name):
        """Get Delphix environment by its name

        :param str name: environment name
        :rtype: delphixpy.v1_6_0.web.vo.Environment
        """
        resources = self._get_all_resources(web.environment)
        return self._find_resource_by_attr(collection=resources, attr_value=name)

    def get_env_by_ip(self, ip_addr):
        # isn't working for now
        # ipdb > web.host.get_all(client._engine)[0]._address

        resources = self._get_all_resources(web.environment)
        return self._find_resource_by_attr(collection=resources, attr_value=ip_addr)

    def get_repository(self, repo_type, env_name):
        """Get

        :param str repo_type: repository type (MSSqlInstance)
        :param str env_name: environment
        :rtype: delphixpy.v1_6_0.web.vo.SourceRepository
        """
        env = self.get_env(env_name)
        repos = web.repository.get_all(engine=self._engine, environment=env.reference)
        return self._find_resource_by_attr(collection=repos, attr_value=repo_type, attr_name="type")

    def get_database(self, name, group_name):
        group = self.get_group(group_name)
        dbs = web.database.get_all(engine=self._engine, group=group.reference)
        return self._find_resource_by_attr(collection=dbs, attr_value=name)

    def delete_database(self, reference):
        # if db.staging == False and db.virtual == True: ??
        web.database.delete(engine=self._engine, ref=reference)

    def provision_vdb(self, env, group, db_name, source_database, vdb_type):

        if vdb_type.lower() not in self._vdb_params_prepare_map:
            raise UnsupportedVDBException("Unknown VDB type {}. Supported types are {}".format(
                vdb_type,
                self._vdb_params_prepare_map.keys()))

        prepare_vdb_params_handler = self._vdb_params_prepare_map[vdb_type.lower()]

        vdb_params = prepare_vdb_params_handler(env=env,
                                                group=group,
                                                db_name=db_name,
                                                source_database=source_database)

        web.database.provision(self._engine, vdb_params)

    def refresh_vdb(self, name, group_name, timestamp=None):

        db = self.get_database(name=name, group_name=group_name)

        if db.reference.lower().startswith("oracle"):
            refresh_params = web.vo.OracleRefreshParameters()
        else:
            refresh_params = web.vo.RefreshParameters()

        source_db = web.database.get(self._engine, db.provision_container)
        timeflow_point_parameters = web.vo.TimeflowPointSemantic()
        timeflow_point_parameters.location = "LATEST_POINT"
        timeflow_point_parameters.container = source_db.reference
        refresh_params.timeflow_point_parameters = timeflow_point_parameters

        web.database.refresh(engine=self._engine, ref=db.reference, refresh_parameters=refresh_params)

    def _find_resource_by_attr(self, collection, attr_value, attr_name="name"):
        """

        :param list collection:
        :param str name:
        :return:
        """
        for resource in collection:
            if getattr(resource, attr_name) == attr_value:
                return resource

        raise NotFoundResourceException("Resource with {} '{}' was not found on the Delphix"
                                        .format(attr_name, attr_value))

    def _prepare_mssql_vdb_params(self, env, group, db_name, source_database):
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

        repo = self.get_repository(repo_type=repo_type, env_name=env.name)
        vdb_params.source_config.repository = repo.reference

        return vdb_params
