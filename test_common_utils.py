from common_utils import clear_string

def test_clear_string():
    
    sin = 'agulha n19'
    sout = 'agulha 19'
    assert clear_string(sin) == sout

    sin = 'Amoxaciclina + clavulanico 156+25mg'
    sout = 'amoxaciclina+clavulanico 156+25mg'
    assert clear_string(sin) == sout

    sin = 'Amoxaciclina + clavulanico 156 + 25mg'
    sout = 'amoxaciclina+clavulanico 156+25mg'
    assert clear_string(sin) == sout

    sin = 'Asa 25mg/67.5mg'
    sout = 'asa 25mg/67,5mg'
    assert clear_string(sin) == sout

    sin = 'Betametazona 0 05%'
    sout = 'betametazona 0,05%'
    assert clear_string(sin) == sout

    sin = 'bromexina (tosse seca)'
    sout = 'bromexina tosse seca'
    assert clear_string(sin) == sout

    sin = 'calcio-gluconato'
    sout = 'calciogluconato'
    assert clear_string(sin) == sout

    sin = 'ciproflaxina /tinizol'
    sout = 'ciproflaxina/tinizol'
    assert clear_string(sin) == sout

    sin = 'Cloreto desodio 0;9%'
    sout = 'cloreto desodio 0,9%'
    assert clear_string(sin) == sout

    sin = 'coartem b6'
    sout = 'coartem b6'
    assert clear_string(sin) == sout

    sin = ' coartem b6'
    sout = 'coartem b6'
    assert clear_string(sin) == sout

    sin = 'coarten b6'
    sout = 'coartem b6'
    assert clear_string(sin) == sout

    sin = 'diclofena'
    sout = 'diclofenac'
    assert clear_string(sin) == sout

    sin = 'enalpril'
    sout = 'enalapril'
    assert clear_string(sin) == sout

    sin = 'Fenitoina 250 mg 5ml'
    sout = 'fenitoina 250mg 5ml'
    assert clear_string(sin) == sout 

    sin = 'gentamicina +Dexametazona 10ml'
    sout = 'gentamicina+dexametazona 10ml'
    assert clear_string(sin) == sout
    
    sin = 'gentamicina crème '
    sout = 'gentamicina creme'
    assert clear_string(sin) == sout

    sin = 'glibenclonide / metoformina'
    sout = 'glibenclonide/metoformina'
    assert clear_string(sin) == sout

    sin = 'hemoclassificador anti-A'
    sout = 'hemoclassificador antia'
    assert clear_string(sin) == sout

    sin = 'Antiacido 500ng'
    sout = 'antiacido 500mg'
    assert clear_string(sin) == sout

    sin = 'artesunato 100mg + amodiaquina 270mg'
    sout = 'artesunato 100mg+amodiaquina 270mg'
    assert clear_string(sin) == sout

    sin = 'Betametazona 0 05%'
    sout = 'betametazona 0,05%'
    assert clear_string(sin) == sout

    sin = 'Ketaconazol30g 2%'
    sout = 'ketaconazol 30g 2%'
    assert clear_string(sin) == sout

    sin = 'ligaduara de gase 10cmx4,5m'
    sout = 'ligaduara de gase 10cmx4,5m'
    assert clear_string(sin) == sout

    sin = 'Ligadura de   gase    15cm'
    sout = 'ligadura de gase 15cm'
    assert clear_string(sin) == sout

    sin = 'mascaras n95'
    sout = 'mascaras 95'
    assert clear_string(sin) == sout

    sin = 'Tramadol+Paracetamol 325 +37:5 mg'
    sout = 'tramadol+paracetamol 325+37,5mg'
    assert clear_string(sin) == sout

    sin = 'vitamina k1'
    sout = 'vitamina k1'
    assert clear_string(sin) == sout

    sin = 'adesivo perforado 7cmx 5cm'
    sout = 'adesivo perforado 7cmx5cm'
    assert clear_string(sin) == sout

    sin = 'f-100'
    sout = 'f100'
    assert clear_string(sin) == sout

    