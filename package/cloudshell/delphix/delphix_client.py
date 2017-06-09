from delphixpy.v1_6_0.delphix_engine import DelphixEngine
from delphixpy.v1_6_0 import web

from cloudshell.delphix.exceptions import UnsupportedVDBException
from cloudshell.delphix.exceptions import NotFoundResourceException


class DelphixClient(object):

    def __init__(self, engine_conf):
        self._vdb_params_prepare_map = {
            "mssql": self._prepare_mssql_vdb_params
        }
        self._engine = self._get_engine(engine_conf)
        self._cache = {}

    def _get_engine(self, engine_conf):
        return DelphixEngine(address=engine_conf.address,
                             user=engine_conf.user,
                             password=engine_conf.password,
                             namespace=engine_conf.namespace)

    def _get_all_resources(self, resource_cls):
        if resource_cls not in self._cache:
            self._cache[resource_cls] = resource_cls.get_all(engine=self._engine)

        return self._cache[resource_cls]

    def get_group(self, name):
        resources = self._get_all_resources(web.group)
        return self._find_resource_by_attr(collection=resources, attr_value=name)

    def get_env(self, name):
        resources = self._get_all_resources(web.environment)
        return self._find_resource_by_attr(collection=resources, attr_value=name)

    def get_env_by_ip(self, ip_addr):
        # isn't working for now
        # ipdb > web.host.get_all(client._engine)[0]._address

        resources = self._get_all_resources(web.environment)
        return self._find_resource_by_attr(collection=resources, attr_value=ip_addr)

    def get_repository(self, repo_type, env_name):
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

    def create_windows_target_env(self, address, user, password, env_name):
        # todo: get user/password from the VM
        envCreateParams = web.vo.HostEnvironmentCreateParameters()
        envCreateParams.primary_user = web.vo.EnvironmentUser()
        envCreateParams.primary_user.name = "qualisystems\delphix_trgt"
        envCreateParams.primary_user.credential = web.vo.PasswordCredential()
        envCreateParams.primary_user.credential.password = "1234qwer!"
        envCreateParams.host_environment = web.vo.WindowsHostEnvironment()
        envCreateParams.host_environment.name = "WINDOWSSOURCE12424"
        # envCreateParams.host_environment.proxy = "WINDOWS_HOST-6"  # This is the Host ID of the Windows Server that houses the connector
        envCreateParams.host_parameters = web.vo.WindowsHostCreateParameters()
        envCreateParams.host_parameters.host = web.vo.WindowsHost()
        envCreateParams.host_parameters.host.address = "192.168.65.69"
        web.environment.create(self._engine, envCreateParams)

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

        repo = self.get_repository(repo_type=repo_type, env_name=env.name)
        vdb_params.source_config.repository = repo.reference

        return vdb_params
