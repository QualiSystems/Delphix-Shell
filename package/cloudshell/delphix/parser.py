class DelphixEngineConfig(object):
    def __init__(self, address, user, password, namespace):
        self.address = address
        self.user = user
        self.password = password
        self.namespace = namespace


def parse_delphix_resource(context):
    """Parse CloudShell context into DelphixEngineConfig model

    :param context:
    :rtype: DelphixEngineConfig
    """
    attrs = context.resource.attributes
    resource = DelphixEngineConfig(address=attrs["address"],
                                   user=attrs["user"],
                                   password=attrs["password"],
                                   namespace=attrs["namespace"])
    return resource
