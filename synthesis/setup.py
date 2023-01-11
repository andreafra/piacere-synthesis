import yaml

from .types import Class, Elem, AssocRel, AttrRel

def setup(metamodel_path: str, doml_path: str, unbound_elems: int = 0):
    with open(metamodel_path, 'r') as mm_file:
        mm = yaml.safe_load(mm_file)
    with open(doml_path, 'r') as im_file:
        im = yaml.safe_load(im_file)
        
    assert mm is not None
    assert im is not None

    # We need to create first the elements by parsing the metamodel
    classes = { f'{cat_k}_{elem_k}' : elem_v
        for cat_k, cat_v in mm.items()
        for elem_k, elem_v in cat_v.items() 
    }

    # Returns a class with all the associations and attributes of its superclasses
    def merge_superclass(elem):
        e_k, e_v = elem
        sc_k = e_v.get('superclass')
        sc_v = classes.get(sc_k)
        if not sc_k:
            e_v['associations'] = {f'{e_k}::{k}': v for k,v in e_v.get('associations',{}).items()}
            e_v['attributes'] = {f'{e_k}::{k}': v for k,v in e_v.get('attributes',{}).items()}
            return e_v
        else:
            e_v['associations'] = {f'{e_k}::{k}': v for k,v in e_v.get('associations',{}).items()} | sc_v.get('associations',{})
            e_v['attributes'] = {f'{e_k}::{k}': v for k,v in e_v.get('attributes',{}).items()} | sc_v.get('attributes',{})
            return e_v

    # all the elements with all the inherited attributes and associations
    merged_classes = { 
        k : merge_superclass((k,v))
        for k,v in classes.items()
    }

    # Create data
    CLASSES = {
        class_k : Class(
            class_k, 
            class_v.get('attributes', {}), 
            class_v.get('associations', {})
        )
        for class_k, class_v in merged_classes.items()
    }

    ELEMS = {
        elem_k : Elem(
            elem_v['id'],
            elem_v['name'],
            elem_v['attrs'],
            elem_v['assocs'],
            CLASSES[elem_v['class']],
        )
        for elem_k, elem_v in im.items()
    }

    # This also helps catching errors in class/assoc names
    ASSOCS = {
        f'{assoc_k}' : AssocRel(class_v, CLASSES[assoc_v['class']], assoc_v.get('inverse_of', None))
        for class_k, class_v in CLASSES.items()
        for assoc_k, assoc_v in class_v.associations.items()
    }

    # Careful: I decided to default multiplicity to 0..1
    ATTRS = {
        f'{attr_k}' : AttrRel(attr_v.get('multiplicity', '0..1'), attr_v['type'])
        for class_k, class_v in CLASSES.items()
        for attr_k, attr_v in class_v.attributes.items()
    }

    ub_elems = { 
        f'elem_ub_{i}' : Elem(
            f'elem_ub_{i}',
            f'Unbound Element #{i}',
            {},
            {},
            unbound=True
        ) 
        for i in range(unbound_elems)
    }

    ELEMS |= ub_elems

    return CLASSES, ELEMS, ASSOCS, ATTRS
