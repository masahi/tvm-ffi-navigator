"""Torch FFI convention"""
import os
from .. import pattern

class TorchProvider:
    """Provider for Torch FFI.

    Parameters
    ----------
    resolver : PyImportResolver
        Resolver for orginial definition.

    logger : Logger object
    """
    def __init__(self, resolver, logger):
        self.resolver = resolver
        self._pypath_root = None
        self.logger = logger

    def _cc_extract(self, path, source, begin, end):
        return []

    def _py_extract(self, path, source, begin, end):
        return []

    def init_pass(self, path, source):
        """This function will be called for each file before extract."""
        if path.endswith("torch/__init__.py"):
            self._pypath_root = os.path.abspath(path[:-len("/__init__.py")])
            self.resolver.add_package("torch", self._pypath_root)
            self.logger.info("Torch: find python path %s", self._pypath_root)

    def extract(self, path, source, begin=0, end=None):
        """This function will be called for each file
        Extract patterns in the file as specified in pattern.py and return them.
        """
        if path.endswith(".cpp") or path.endswith(".h"):
            self.logger.info("Extracting from %s", path)
            return self._cc_extract(path, source, begin, end)
        return []

    def extract_symbol(self, path, source, pos):
        """Extract possible pattern in the specified location, if not found, return None."""
        # only search a small context
        begin = max(pos.line - 1, 0)
        end = min(pos.line + 2, len(source))
        # We can use extract and verify to get the pattern.
        if path.endswith(".py"):
            for res in self._py_extract(path, source, begin, end):
                if (isinstance(res, (pattern.Ref, pattern.Def)) and
                    res.range.start.line <= pos.line and
                    res.range.end.line >= pos.line and
                    res.range.start.character <= pos.character and
                    res.range.end.character >= pos.character):
                    return res
        return None

    def get_additional_scan_dirs(self, root_path):
        return [
            os.path.join(root_path, "aten", "src", "ATen"),
            os.path.join(root_path, "torch")
        ]
