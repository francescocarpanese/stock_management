import re


def is_positive_null_integer(s):
    try:
        num = int(s)
        return num >= 0
    except ValueError:
        return False


def is_positive_integer(s):
    try:
        num = int(s)
        return num > 0
    except ValueError:
        return False


def parse_dose_units(s):
    name = s
    dose = ""
    units = ""

    # Check is type <name><space><number><units>
    pattern = r"\b(.+)\s(\d{1,4})([a-zA-Z]{1,4})(?=\s|$)\b"

    # Find how many time <number up to 4 digirs><word up to 4 letters> appears in the string
    pattern_doseunits = r"\b(\d{1,4})([a-zA-Z]{1,2})\b"

    match = re.match(pattern, s)
    if match and len(re.findall(pattern_doseunits, s)) == 1:
        dose = match.group(2)
        units = match.group(3)
        name = s.replace(dose + units, "")
        name = re.sub(r"\s+", " ", name)
        name = name.strip()

    # Check is type <name><space><number>,<number><units>
    pattern = r"\b(.+)\s(\d{1,4},\d{1,4})([a-zA-Z]{1,4})(?=\s|$)\b"
    match = re.match(pattern, s)
    if match and len(re.findall(pattern_doseunits, s)) == 1:
        dose = match.group(2)
        units = match.group(3)
        name = s.replace(dose + units, "")
        name = re.sub(r"\s+", " ", name)
        name = name.strip()

    return name, dose, units


def clear_string(s):
    # Trim the string
    s = s.strip()
    # lower case the string
    s = s.lower()
    # replace all accents
    s = s.replace("á", "a")
    s = s.replace("ã", "a")
    s = s.replace("é", "e")
    s = s.replace("è", "e")
    s = s.replace("ê", "e")
    s = s.replace("í", "i")
    s = s.replace("ó", "o")
    s = s.replace("ô", "o")
    s = s.replace("õ", "o")
    s = s.replace("ú", "u")
    s = s.replace("ç", "c")

    # if string contains 'n' in any position follow by a digit, strip the 'n', keep the digit
    s = re.sub(r"n(\d)", r"\1", s)

    # if string contains a char with digit attached, add a space between them, unless the char is 'b'
    s = re.sub(r"([a-z])(\d)", r"\1 \2", s)

    # if string contains a digit followed by `ng`, replace it with `mg`
    s = re.sub(r"(\d)ng", r"\1mg", s)

    # if string contains ';' between two digits, replace it with a ','
    s = re.sub(r"(\d);(\d)", r"\1,\2", s)

    # if string contains a '(' or ')', remove it
    s = re.sub(r"[\(\)]", " ", s)

    # if a string contains a number followed by a space and then [mg, ml, g, l, mg, gr, cl], remove the space
    s = re.sub(r"(\d) (mg|ml|g|l|mg|gr|cl)", r"\1\2", s)

    # remove all `-` and `_`
    s = re.sub(r"[-_]", "", s)

    # if string contains ':' between two digits, replace it with a ','
    s = re.sub(r"(\d):(\d)", r"\1,\2", s)

    # if string contains double 'z', replace it with a single 'z'
    s = re.sub(r"zz", r"z", s)

    # replace 'xerope' with 'xarope'
    s = re.sub(r"xerope", r"xarope", s)

    # replace 'coarten' with 'coartem'
    s = re.sub(r"coarten", r"coartem", s)

    # replace 'diclofena' with 'diclofenac'
    s = re.sub(r"diclofena", r"diclofenac", s)

    # replace 'enalpril' with 'enalapril'
    s = re.sub(r"enalpril", r"enalapril", s)

    # replace 'eritomicina' with 'eritromicina'
    s = re.sub(r"eritomicina", r"eritromicina", s)

    # replace 'ertromicina' with 'eritromicina'
    s = re.sub(r"ertromicina", r"eritromicina", s)

    # replace 'bezoico' with 'benzoico'
    s = re.sub(r"bezoico", r"benzoico", s)

    # replace 'perfurado' with 'perforado'
    s = re.sub(r"perfurado", r"perforado", s)

    # replace 'aldipina' with 'amlodipina'
    s = re.sub(r"aldipina", r"amlodipina", s)

    # replace 'amoxacilina' with 'amoxicilina'
    s = re.sub(r"amoxacilina", r"amoxicilina", s)

    # replace 'amoxacilina' with 'amoxicilina'
    s = re.sub(r"amoxacilina", r"amoxicilina", s)

    # replace 'amoxaclina' with 'amoxicilina'
    s = re.sub(r"amoxaclina", r"amoxicilina", s)

    # replace 'emoroid' with 'hemorroid'
    s = re.sub(r"emoroid", r"hemorroid", s)

    # replace 'emorroid' with 'hemorroid'
    s = re.sub(r"emorroid", r"hemorroid", s)

    # if thre a '/' between to spaces, remove the spaces
    s = re.sub(r" / ", r"/", s)

    # replace 'enalpil' with 'enalapril'
    s = re.sub(r"enalpil", r"enalapril", s)

    # replace 'artensuato' with 'artesunato'
    s = re.sub(r"artensuato", r"artesunato", s)
    s = re.sub(r"artensuato", r"artesunato", s)
    s = re.sub(r"arthesunato", r"artesunato", s)
    s = re.sub(r"arthesunato", r"artesunato", s)
    s = re.sub(r"artesunate", r"artesunato", s)
    s = re.sub(r"artesonato", r"artesunato", s)
    s = re.sub(r"artesinato", r"artesunato", s)

    # replace most common misspellings of 'amoxaciclina'
    s = re.sub(r"amoxiciclina", r"amoxaciclina", s)
    s = re.sub(r"amoxiciclina", r"amoxaciclina", s)
    s = re.sub(r"amoxacilin", r"amoxaciclina", s)
    s = re.sub(r"amoxacilin", r"amoxaciclina", s)
    s = re.sub(r"amoxacilna", r"amoxaciclina", s)

    # replace most common misspellings of 'supositorio'
    s = re.sub(r"supozitorio", r"supositorio", s)
    s = re.sub(r"supositorio", r"supositorio", s)
    s = re.sub(r"supozitorio", r"supositorio", s)
    s = re.sub(r"supositorioo", r"supositorio", s)
    s = re.sub(r"supositoria", r"supositorio", s)

    # replace misplellings of 'buscopam'
    s = re.sub(r"buscopan", r"buscopam", s)
    s = re.sub(r"buscompan", r"buscopam", s)

    # replace misplellings of 'ceftriazona'
    s = re.sub(r"cetfriasona", r"ceftriazona", s)

    # remove space when find 'b 6'
    s = re.sub(r"b 6", r"b6", s)

    # remove a space when find 'b 12'
    s = re.sub(r"b 12", r"b12", s)
    s = re.sub(r"b 18", r"b18", s)
    s = re.sub(r"b 24", r"b24", s)

    # replace 'comprenssas' with 'compressas'
    s = re.sub(r"comprenssas", r"compressas", s)

    # replace 'sterile' with 'esteril'
    s = re.sub(r"sterile", r"esteril", s)

    # replace 'dexametasone' with 'dexametazona'
    s = re.sub(r"dexametasone", r"dexametazona", s)

    # replace 'cc' with 'c'
    s = re.sub(r"cc", r"c", s)

    # remove a space when find 'k 1'
    s = re.sub(r"k 1", r"k1", s)

    # remove a space when find 'k 12'
    s = re.sub(r"k 12", r"k12", s)

    # remove space in `f 75`
    s = re.sub(r"f 75", r"f75", s)

    # remove space in `f 100`
    s = re.sub(r"f 100", r"f100", s)

    # add space after flindix
    s = re.sub(r"flindix", r"flindix ", s)

    # replace metronidazole with metronidazol
    s = re.sub(r"metronidazole", r"metronidazol", s)

    # replace neurobiom with neurobion
    s = re.sub(r"neurobiom", r"neurobion", s)

    # repalce 'supposto' with 'supositorio'
    s = re.sub(r"supposto", r"supositorio", s)

    # remove a space when find 'k 2'
    s = re.sub(r"k 2", r"k2", s)

    # replae 'seeringa' with 'seringa'
    s = re.sub(r"seeringa", r"seringa", s)
    s = re.sub(r"seringas", r"seringa", s)

    # replace 'shaltoux1' with 'shaltoux 1'
    s = re.sub(r"shaltoux1", r"shaltoux 1", s)

    # replace 'ciproflox' with 'ciproflox '
    s = re.sub(r"ciproflox", r"ciproflox ", s)

    # replace 'oux' with 'oux '
    s = re.sub(r"oux", r"oux ", s)

    # replace '.' with ',' between two digits
    s = re.sub(r"(\d)\.(\d)", r"\1,\2", s)

    # Remove all special characters, but allow ',','+','/','%'
    s = re.sub(r"[^a-zA-Z0-9,+/%]", r" ", s)

    # replace 'teste' with 'test'
    s = re.sub(r"teste", r"test", s)

    # if there is a space, followed by 'n' followed by space, remove the 'n'
    s = re.sub(r" n ", r" ", s)

    # replace all ';' with ','
    s = re.sub(r";", r",", s)

    # if there is a . between two digits, replace it with a ,
    s = re.sub(r"(\d)\.(\d)", r"\1,\2", s)

    # all multiple spaces to a single space
    s = re.sub(r"\s+", " ", s)

    # if there is a space followed by '/', remove the space
    s = re.sub(r" /", r"/", s)

    # if thre is an 'x' preceded by a charachter, and followed by a space, remove the space
    s = re.sub(r"([a-z])x ", r"\1x", s)

    # if there is a 0 preceded by a space, and followed by a space, than another 0, insert a comma between the two 0
    s = re.sub(r" 0 0", r" 0,0", s)

    # trim the string again
    s = s.strip()

    return s
