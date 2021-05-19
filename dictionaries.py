




def merge_dicts(d1: dict, d2: dict) -> dict:
    d_new = d1.copy()
    d_new.update(d2)
    return d_new


def lists_to_dict(l_keys: list, l_vals: list) -> dict:
    return dict(zip(l_keys, l_vals))

# For building a dict from lists where the items need modification or validation
def lists_comprehend_dict(l_keys: list, l_vals: list) -> dict:
    def key_fn(key):
        # do thing to key
        return key
    def val_fn(val):
        # do thing to val
        return val
        #key_fn(key): val_fn(val)
    return {key: val for (key, val) in zip(l_keys, l_vals)}


def display(d: dict) -> None:
    import json
    print(json.dumps(d, indent=4))


def sort_dict_list(l_dicts: list, key) -> list:
    l_dicts.sort(key=lambda item: item.get(key))


if __name__ == '__main__':
    # test
    d_test = {
        'k1': 'v1',
        'k2': 'v2',
        'k3': {
            'k3-1': 'v3-1',
            'k3-2': 'v3-2',
            }
        }

    display(d_test)