from js9 import j

class AYSable:
    """
    Abstract implementation for class that reflect an AYS service.
    class should have a name and actor attributes

    This provide common method to CRUD AYS service from the python classes
    """
    @property
    def name(self):
        return self._obj.name

    @property
    def role(self):
        return self.actor.split('.')[0]

    def create(self, aysrepo):
        """
        create the AYS Service
        """
        raise NotImplementedError()

    def get(self, aysrepo):
        """
        get the AYS service
        """
        try:
            return aysrepo.serviceGet(role=self.role, instance=self.name)
        except j.exceptions.NotFound:
            raise ValueError("Could not find {} with name {}".format(self.role, self.name))
