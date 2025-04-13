def from_csv(cls, data):
    results = []
    for row in data:
        kwargs = {}
        for remote_key, local_key in cls.MAP.items():
            if remote_key.startswith("__"):
                kwargs[local_key] = None
            else:
                if remote_key not in row:
                    kwargs[local_key] = None
                else:
                    val = row[remote_key].strip()
                    kwargs[local_key] = val

        results.append(cls(**kwargs))

    return results
