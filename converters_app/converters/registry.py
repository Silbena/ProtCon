from os import path
import converters.converters as convList

def initRegistry() -> dict:
    converters = convList.get_converters()

    registry = {}
    for conv in converters:
        key = conv.IN_EXTENSION + conv.OUT_EXTENSION
        if key in registry:
            print(f'Failed to register {conv}, duplicate key [{key}]')
            return None
        else:
            registry[key] = conv

    return registry


def getKey(in_filename : str, out_filename : str) -> str:
    _, in_ext = path.splitext(in_filename)
    _, out_ext = path.splitext(out_filename)

    return in_ext + out_ext
    