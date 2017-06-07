class DelphixClientException(Exception):
    """Base Delphix client exception"""
    pass


class UnsupportedVDBException(DelphixClientException):
    """Unsupported VDB type for provision"""
    pass


class NotFoundResourceException(DelphixClientException):
    """Unable to find resource on the Delphix"""
    pass
