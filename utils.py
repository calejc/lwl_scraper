# Helper utility functions


# Return player's name from LWL jersey links
def parse_link(link):
    to_replace = ['=', '%20', '&']
    for item in to_replace:
        link = link.replace("{}".format(item), " ", 1)
    link = link.split()
    name = link[1] + " " + link[2]
    return name

# Check if a value exists in nested dict
def check_value(data, value):
    tmp = []
    for ele in data.values():
        if isinstance(ele,dict):
            for k, v in ele.items():
                if isinstance(v, dict):
                    for ke, va in v.items():
                        tmp.append(va)
                else:
                    tmp.append(v)
    if value in tmp:
        return True
    else:
        return False

# Return a different key-value pair inside a nested dict key
def return_alt(d, value, requested_alt):
    for k, v in d.items():
        if isinstance(v, dict):
            p = return_alt(v, value, requested_alt)
            if p:
                return d[k][requested_alt]
        elif v == value:
            return k
