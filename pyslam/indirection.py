
class CategoryMapper(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reverse_map = {v: k for k, v in self.items()}

    def __setitem__(self, key, value):
        # Si la clé existe déjà, on supprime l'ancienne association dans le reverse map
        if key in self:
            del self._reverse_map[self[key]]

        # Si la valeur existe déjà, on supprime l'ancienne association dans le reverse map
        if value in self._reverse_map:
            del self._reverse_map[value]

        super().__setitem__(key, value)
        self._reverse_map[value] = key

    def __delitem__(self, key):
        value = self[key]
        super().__delitem__(key)
        del self._reverse_map[value]

    def get_key(self, value):
        return self._reverse_map.get(value)


class Indirection:

    def __init__(self, mapper: CategoryMapper, indirections: dict) -> None:
        self.mapper = mapper
        self.indirections = indirections

    def out_value(self, key, in_value):
        assert in_value in self.indirections, "this value is not defined in indirected map"
        assert key in self.mapper, "this key is not defined in indirected map"
        return self.indirections[in_value][self.mapper[key]]
