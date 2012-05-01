class RepartedError(Exception):
    """
    Base Exception
    """
    def __init__(self, code):
        self._register(code, code_dict=None)

    def _register(self, code, code_dict):
        self.code_dict = code_dict
        self.code = code

    def __str__(self):
        return repr(self.code_dict.get(self.code, None))

size_error_code = {
    400: "Device instance required for this operation.",
    401: "Invalid length type."
}

device_error_code = {
    500: "No device found."
}

disk_error_code = {
    600: "Failed to initialize disk.",
    601: "Failed to commit to device.",
    602: "Failed to commit to OS.",
    603: "Unsupported disk label.",
    604: "Failed to get disk type.",
    605: "Failed to create new disk.",
    606: "Method unavailable for initialized disk."
}

partition_error_code = {
    700: "Failed to initialize partition.",
    701: "Failed to add partition to disk.",
    702: "Failed to set user-defined constraint to disk.",
    703: "Failed to set device constraint to disk.",
    704: "Failed to set partition name to disk.",
    705: "Invalid partition instance or partition number.",
    706: "Partition is busy.",
    707: "Invalid partition type.",
    708: "Invalid alignment option.",
    709: "Invalid geometry.",
    710: "Unsupported flag.",
}

class SizeError(RepartedError):
    def __init__(self, code):
        self._register(code, size_error_code)

class DeviceError(RepartedError):
    def __init__(self, code):
        self._register(code, device_error_code)

class DiskError(RepartedError):
    def __init__(self, code):
        self._register(code, disk_error_code)

class DiskCommitError(RepartedError):
    def __init__(self, code):
        self._register(code, disk_error_code)

class PartitionError(RepartedError):
    def __init__(self, code):
        self._register(code, partition_error_code)

class AddPartitionError(RepartedError):
    def __init__(self, code):
        self._register(code, partition_error_code)

class DeletePartitionError(RepartedError):
    def __init__(self, code):
        self._register(code, partition_error_code)