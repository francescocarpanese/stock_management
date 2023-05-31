from common_utils import clear_string, parse_dose_units
import pytest

@pytest.mark.parametrize("sin, sout", [
    ('', ''),
    (' ', ''),
    ('  ', ''),
    ('agulha n19', 'agulha 19'),
    ('Amoxaciclina + clavulanico 156+25mg','amoxaciclina + clavulanico 156+25mg'),
    ('Amoxaciclina + clavulanico 156 + 25mg','amoxaciclina + clavulanico 156 + 25mg'),
    ('Asa 25mg/67.5mg','asa 25mg/67,5mg'),
    ('Betametazona 0 05%','betametazona 0,05%'),
    ('bromexina (tosse seca)','bromexina tosse seca'),
    ('calcio-gluconato','calciogluconato'),
    ('ciproflaxina /tinizol','ciproflaxina/tinizol'),
    ('Cloreto desodio 0;9%','cloreto desodio 0,9%'),
    ('coartem b6','coartem b6'),
    (' coartem b6','coartem b6'),
    ('coarten b6','coartem b6'),
    ('diclofena','diclofenac'),
    ('enalpril','enalapril'),
    ('Fenitoina 250 mg 5ml','fenitoina 250mg 5ml'),
    ('gentamicina +Dexametazona 10ml','gentamicina +dexametazona 10ml'),
    ('gentamicina crème ','gentamicina creme'),
    ('glibenclonide / metoformina','glibenclonide/metoformina'),
    ('hemoclassificador anti-A','hemoclassificador antia'),
    ('Antiacido 500ng','antiacido 500mg'),
    ('artesunato 100mg + amodiaquina 270mg','artesunato 100mg + amodiaquina 270mg'),
    ('Betametazona 0 05%','betametazona 0,05%'),
    ('Ketaconazol30g 2%','ketaconazol 30g 2%'),
    ('ligaduara de gase 10cmx4,5m','ligaduara de gase 10cmx4,5m'),
    ('Ligadura de   gase    15cm','ligadura de gase 15cm'),
    ('mascaras n95','mascaras 95'),
    ('Tramadol+Paracetamol 325 +37:5 mg','tramadol+paracetamol 325 +37,5mg'),
    ('vitamina k1','vitamina k1'),
    ('adesivo perforado 7cmx 5cm','adesivo perforado 7cmx5cm'),
    ('f-100','f100'),
])
def test_clear_string(sin, sout):
    assert clear_string(sin) == sout


@pytest.mark.parametrize("input_string, expected_output", [
    ("hidralazina 20mg", ("hidralazina", "20", "mg")),
    ("hidralazina 20 mg", ("hidralazina 20 mg", "", "")),
    ("hidrocortiazida+losardiac 100/25mg", ("hidrocortiazida+losardiac 100/25mg", "", "")),
    ('ibucap forte', ('ibucap forte', '', '')),
    ('iodopovidona 1% 500ml', ('iodopovidona 1%', '500', 'ml')),
    ('ketaconazol 30g 2%', ('ketaconazol 2%', '30', 'g')),
    ('lidocaina 20%', ('lidocaina 20%', '', '')),
    ('ligaduara de gase 10cmx4,5m', ('ligaduara de gase 10cmx4,5m', '', '')),
    ('losardiac 100mg/25mg', ('losardiac 100mg/25mg', '', '')),
    ('paracetamol 125mg 5ml', ('paracetamol 125mg', '5', 'ml')),
    ('paracetamol 500mg efervescentes', ('paracetamol efervescentes', '500', 'mg')),
    ('penicilina benzatina 2,4mg', ('penicilina benzatina', '2,4', 'mg')),
    ('shaltoux125ml', ('shaltoux125ml', '', '')),
    ('sulfadiaxina 500mg+25 pirimemina', ('sulfadiaxina 500mg+25 pirimemina', '', '')),
    ('artesunato 100mg + amodiaquina 270mg', ('artesunato 100mg + amodiaquina 270mg', '', '')),
])
def test_parse_dose(input_string, expected_output):
    parsed =  parse_dose_units(input_string)
    assert parsed == expected_output
     