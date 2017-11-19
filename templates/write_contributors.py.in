# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Generates CONTRIBUTORS.rst file, with the name and email of the contributors
# to the proejct, sorted from more to less commits.

import subprocess

SRC = "${buildout:directory}/bika/lims"
OUTFILE = SRC + '/CONTRIBUTORS.rst'

# User names or emails to be replaced. If the value is None, the committer will
# not be listed in the list of contributors
REPLACEMENTS = {
    'Alexander':                 'Alexander Karlsson',
    'Ammy2':                     'Aman Arora',
    'Anneline Sweetnam':         'Anneline Sweetname',
    'Campbell Mc Kellar-Basset': 'Campbell McKellar-Basset',
    'Campbell MccKellar-Basset': 'Campbell McKellar-Basset',
    'Campbell':                  'Campbell McKellar-Basset',
    'Espurna':                   'Pau Soliva',
    'GitHub':                    None, # Ommit GitHub commits
    'Hocine':                    'Hocine Bendou',
    'Jordi Puiggené Valls':      'Jordi Puiggené',
    'Nihadness':                 'Nihad Mammadli',
    'Pau Soliva Dueso':          'Pau Soliva',
    'Pieter':                    'Pieter van der Merwe',
    'Soliva':                    'Pau Soliva',
    'admin@bikalabs.com':        None,
    'aleksandrmelnikov':         'Aleksandr Melnikov',
    'anneline':                  'Anneline Sweetname',
    'campbellbasset':            'Campbell McKellar-Basset',
    'hocine':                    'Hocine Bendou',
    'hocinebendou':              'Hocine Bendou',
    'jordi@zeus':                None,
    'karnatijayadeep':           'Jayadeep Karnati',
    'lemoene':                   'Lemoene',
    'pietercvdm':                'Pieter van der Merwe',
    'ramonski':                  'Ramon Bartl',
    'root@lynn':                 None,
    'zylinx':                    'Alexander Karlsson',
}


def resolve_contributor(contributor):
    if not contributor:
        return None, None
    tokens = contributor.split('|')
    name = tokens[0]
    email = tokens[1]
    if (name in REPLACEMENTS and not REPLACEMENTS[name]) \
            or (email in REPLACEMENTS and not REPLACEMENTS[email]):
        return None, None

    name = REPLACEMENTS.get(name, name)
    email = REPLACEMENTS.get(email, email)
    return name, email


if __name__ == "__main__":

    # Commits sorted from more recent to oldest, with committer name and email
    # The sorting by number of commits reverse will be done later, but we need
    # this initial list sorted this way, cause if there is a duplicate, we want
    # the last email used by that contributor.
    command = "git log --all --format=%cn|%ce"

    # Resolve contributors and build a contributors dictionary, with the number
    # of commits for each contributor
    contributors = subprocess.check_output(command.split(' '), cwd=SRC)
    contributors = contributors.split('\n')
    contributors_dict = dict()
    for contributor in contributors:
        name, email = resolve_contributor(contributor)
        if not name:
            continue
        if name in contributors_dict:
            contributors_dict[name]['commits']+=1
        else:
            contributors_dict[name] = {
                'name': name,
                'email': email,
                'commits': 1,
            }

    # Sort by number of commits reverse
    contributors_sorted = sorted(contributors_dict.items(),
                                 key=lambda x: x[1]['commits'],
                                 reverse=True)

    # Write the file of contributors
    lines = ['Contributors\n', '============\n', '\n']
    for contributor in contributors_sorted:
        name = contributor[1]['name']
        email = contributor[1]['email']
        commits = contributor[1]['commits']
        line = "- {}, {}\n".format(name, email)
        lines.append(line)

    outfile = open(OUTFILE, "w")
    outfile.writelines(lines)
