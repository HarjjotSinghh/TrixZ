import re

def clean(string, deaden_links = False):
    zerospace = "​"
    if deaden_links:
        matches = re.finditer(r"(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?", string)
        matches = set([x.group(0) for x in matches])
        for match in matches:
            string = string.replace(match, "<{}>".format(match))
    return string.replace("@everyone", "@{}everyone".format(zerospace)).replace("@here", "@{}here".format(zerospace))