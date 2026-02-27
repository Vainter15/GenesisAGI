class BaseClass:
    def base_method(self):
        return "base"

class DerivedClass(BaseClass):
    def derived_method(self):
        return "derived"

def simple_function():
    return "simple"

def complex_function():
    return simple_function() + DerivedClass().derived_method()

CONFIG = {
    "setting": "value",
    "nested": {
        "key": "value"
    }
}

def config_dependent_function():
    return CONFIG["setting"] + "_modified"