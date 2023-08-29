class Account:
    def _get_vcpu_h(self):
        vcpu_h = 0

        for _, instance in self.instances.items():
            vcpu_h += instance.vcpu_h

        return vcpu_h

    vcpu_h = property(_get_vcpu_h)

    def __init__(self, data: dict):
        self.id = data['Id']
        self.is_main = data['isMain']
        self.name = data['Name'] if 'Name' in data else ''
        self.instances = {}
        self.lt = {}
        self.asg = {}

    def set_resources(self, instances, lt, asg):
        self.instances = instances
        self.lt = lt
        self.asg = asg
