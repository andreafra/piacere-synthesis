from doml_synthesis.types import Class, Elem, AssocRel, AttrRel, State


def init_data(state: State, metamodel: str, doml: str):
    mm = metamodel
    im = doml

    assert mm is not None
    assert im is not None

    # We need to create first the elements by parsing the metamodel
    classes = {f'{cat_k}_{elem_k}': elem_v
               for cat_k, cat_v in mm.items()
               for elem_k, elem_v in cat_v.items()
               }

    # Returns a class with all the associations and attributes of its superclasses
    def merge_superclass(elem):
        e_k, e_v = elem
        sc_k = e_v.get('superclass')
        sc_v = classes.get(sc_k)
        if not sc_k:
            e_v['associations'] = {f'{e_k}::{k}': v for k,
                                   v in e_v.get('associations', {}).items()}
            e_v['attributes'] = {f'{e_k}::{k}': v for k,
                                 v in e_v.get('attributes', {}).items()}
            return e_v
        else:
            e_v['associations'] = {f'{e_k}::{k}': v for k, v in e_v.get(
                'associations', {}).items()} | sc_v.get('associations', {})
            e_v['attributes'] = {f'{e_k}::{k}': v for k, v in e_v.get(
                'attributes', {}).items()} | sc_v.get('attributes', {})
            return e_v

    # all the elements with all the inherited attributes and associations
    merged_classes = {
        k: merge_superclass((k, v))
        for k, v in classes.items()
    }

    # Create data
    state.data.Classes = {
        class_k: Class(
            class_k,
            class_v.get('attributes', {}),
            class_v.get('associations', {})
        )
        for class_k, class_v in merged_classes.items()
    }

    state.data.Elems = {
        elem_k: Elem(
            elem_v['id'],
            elem_v['name'],
            elem_v['attrs'],
            {k: set(v) for k, v in elem_v['assocs'].items()},
            state.data.Classes[elem_v['class']],
        )
        for elem_k, elem_v in im.items()
    }

    # This also helps catching errors in class/assoc names
    state.data.Assocs = {
        f'{assoc_k}': AssocRel(class_v, state.data.Classes[assoc_v['class']], assoc_v.get('inverse_of', None))
        for class_k, class_v in state.data.Classes.items()
        for assoc_k, assoc_v in class_v.associations.items()
    }

    # Careful: I decided to default multiplicity to 0..1
    state.data.Attrs = {
        f'{attr_k}': AttrRel(attr_v.get('multiplicity', '0..1'), attr_v['type'])
        for class_k, class_v in state.data.Classes.items()
        for attr_k, attr_v in class_v.attributes.items()
    }

    return state
