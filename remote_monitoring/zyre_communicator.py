from pyre_communicator.base_class import PyreBaseCommunicator

class ZyreWebCommunicator(PyreBaseCommunicator):
    def __init__(self, node_name, groups, data_query_timeout=10.):
        super(ZyreWebCommunicator, self).__init__(node_name, groups, [])
        self.data_query_timeout = data_query_timeout
