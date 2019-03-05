from schemas import ma

class FieldSelectionSchema(ma.Schema):
    class Meta:
        fields = ('fields',)

class FilterOrderSelectSchema(ma.Schema):
    class Meta:
        fields = ('fields', 'filter[*]', 'sort')