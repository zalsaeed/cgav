"""Generic 'settings' class can be accessed by low-level modules
but can contain values set by higher-level modules that have access
to CLI and types that are not visible at a low level.
"""
import io
import logging

import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    logging.info("Using pure Python version of yaml loader")
    from yaml import Loader, Dumper


class Settings:
    """Basically a key-value store, with a few bells and whistles."""
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.values = {}
        self.conversions: dict[str, dict[str, object]] = {}

    def __getitem__(self, item: str) -> object:
        """
        Make it look like a dict, not like an object, to
        avoid infinite recursion on getattribute (because of access to self.values,
        which in turn calls get)
        """
        return self.values.get(item)

    def __setitem__(self, key: str, value: object):
        self.values[key] = value

    def read_yaml(self, f: io.IOBase):
        data = yaml.load(f, Loader=Loader)
        assert isinstance(data, dict), f"Configuration file {f} does not represent a table"
        for key, value in data.items():
            self.values[key] = value

    def string_val(self, key: str) -> str:
        """Return string form of a field that has been substituted"""
        assert key in self.values
        if key not in self.conversions:
            return str(self.values[key])
        # It should be among the conversions, which we must search
        # sequentially since the value may not be hashable
        internal_value = self.values[key]
        for named_value, conversion in self.conversions[key].items():
            if internal_value is conversion:
                return named_value
        else:
            raise ValueError(f"Could not back-translate internal value for setting {key}")

    def dump_yaml(self) -> str:
        dumpable = self.values.copy()
        for convertable in self.conversions:
            if convertable in dumpable:
                dumpable[convertable] = self.string_val(convertable)
        return yaml.dump(dumpable, Dumper=Dumper)

    def substitute(self, substitutions: dict[str, dict[str, object]]):
        """Substitute named values, one of which must be present.
        {'k' : {'v1': s1, 'v2': s2}} means
        substitute v1 for s1 in attribute k,
        substitute v2 for s2 in attribute k,
        error if value of 'k' is not among those named values.
        Stashed in self.conversions for reverse conversion on output.
        """
        # For parsed values
        for attr, subs in substitutions.items():
            assert attr in self.values, f"Can't substitute for {attr}, not present in settings"
            value_name = self.values[attr]
            assert value_name in subs, f"{value_name} is not a known name for a {attr} value"
            self.values[attr] = subs[value_name]
        # For dumping values, we save each substitution for reversal
        for attr, subs in substitutions.items():
            self.conversions[attr] = subs

    @staticmethod
    def dump_yaml_from_dict(values: dict, output_dir: str):
        with open(output_dir, 'w') as outfile:
            yaml.dump(values, outfile, Dumper=Dumper, allow_unicode=True, default_flow_style=False)
