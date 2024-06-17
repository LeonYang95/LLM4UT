class UncompilableWhileTestException(Exception):
    """
    在执行测试时，没有能够通过编译，这个理应是不会出现的，出现的话就表示有问题，需要检查。
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class TestResultNotFoundException(Exception):
    """
    在执行测试时，没有找到测试结果，这个理应是不会出现的，出现的话就表示有问题，需要检查。
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class JacocoFailedException(Exception):
    """
    在收集覆盖率时，jacoco没有能够成功执行，需要检查
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class FailButTestOKException(Exception):
    """
    在执行测试时，测试失败了，但是测试结果是OK的，这个理应是不会出现的，出现的话就表示有问题，需要检查。
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class PassButFailException(Exception):
    """
    在执行测试时，测试通过了，但是测试结果是Fail的，这个理应是不会出现的，出现的话就表示有问题，需要检查。
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class MethodNotFoundInJacocoException(Exception):
    """
    在收集覆盖率时，根据函数名没有找到对应的覆盖率信息
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class ParameterNotFoundException(Exception):
    """
    在收集覆盖率时，根据函数名没有找到对应的覆盖率信息
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class EmptyTestClassFailedCompileException(Exception):
    """
    虽然已经指定了空的测试类，但是仍然没能够通过编译
    """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

def NoneTestClassDefinedException(Exception):
    """
    没有定义测试类
    """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg