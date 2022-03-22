#!/usr/bin/python

import re, sys
from pyparsing import (
    Forward,
    Group,
    OneOrMore,
    Optional,
    ParserElement,
    Regex,
    StringEnd,
    Suppress,
    White,
)

ParserElement.setDefaultWhitespaceChars('')

class package(dict):
    def __repr__(self):
        return ''.join([
            self['block'] or '',
            self['operator'] or '',
            self['category'] or '',
            '/',
            self['package'] or '',
            '-' if self['version'] else '',
            self['version'] or '',
            ':' if self['slot'] else '',
            self['slot'] or '',
            '/' if self['subslot'] else '',
            self['subslot'] or '',
            '[' if self['usedep'] else '',
            self['usedep'] or '',
            ']' if self['usedep'] else ''
        ])

def transform(string, location, tokens):
    return package(tokens)

package_dependency = Regex(r'''
    (?P<block>!!?)?
    (?P<operator>[<>]=?|[=~])?
    (?P<category>[\w_][\w+_.-]*)
    /
    (?P<package>[\w_][\w+_]*(?:(?:-[\w_][\w+_]*)*?))
    (?:
        -(?P<version>[\d]+(?:\.[\d]+)*[a-z]?(?:(?:_alpha|_beta|_pre|_rc|_p)[\d]*)*(?:-r[\d]+)?\*?)
    )?
    (?=(?:$|[\s:\[]))
    (?:
        :(?P<slot>[*=]|[\w_][\w+_.-]*=?)
        (?:
            /(?P<subslot>[*=]|[\w_][\w+_.-]*=?)
        )?
    )?
    (?:\[
        (?P<usedep>
            (?:
                 [\w][\w+_@-]*(?:\([+-]\))?[?=]? |
                ![\w][\w+_@-]*(?:\([+-]\))?[?=]  |
                -[\w][\w+_@-]*(?:\([+-]\))?
            )
            (?:,(?:
                 [\w][\w+_@-]*(?:\([+-]\))?[?=]? |
                ![\w][\w+_@-]*(?:\([+-]\))?[?=]  |
                -[\w][\w+_@-]*(?:\([+-]\))?
            ))*
        )
    \])?
''', flags=re.VERBOSE).setParseAction(transform)

dependency_list = Forward()
nested_dependency = (
    Optional(
        Regex(r'\|\||!?[\w][\w+_@-]*\?') + Suppress(OneOrMore(White()))
    ) +
    Suppress('(') +
    Suppress(OneOrMore(White())) + dependency_list +
    Suppress(')')
)
dependency_list <<= OneOrMore(
    (package_dependency | Group(nested_dependency)) +
    Suppress(OneOrMore(White()) | StringEnd())
)

dependency_spec = Optional(dependency_list)

def main():
    success = True
    result = dependency_list.runTests("""
        media-fonts/font-adobe-100dpi
        media-fonts/font-adobe-100dpi-1
        media-fonts/font-adobe-100dpi-1.0
        media-fonts/font-adobe-100dpi-1:1
        media-fonts/font-adobe-100dpi-1[X]
        sys-libs/readline:0/8
        acct-group/apt-cacher-ng
        ( a? ( || ( x11-libs/libA1 x11-libs/libA2 ) b? ( x11-libs/libB ) ) )
        x11-libs/gtk+:3
        x11-libs/gtk+-3.24
        ~x11-libs/gtk+-3.24
        !x11-libs/gtk+-3.24
        !~x11-libs/gtk+-3.24
        !~x11-libs/gtk+-3.24:*
        !~x11-libs/gtk+-3.24:=
        !~x11-libs/gtk+-3.24:3
        !~x11-libs/gtk+-3.24:3=
        !~x11-libs/gtk+-3.24:myslot3=

        x11-libs/gtk+-3.24[X]
        x11-libs/gtk+-3.24[-X]
        x11-libs/gtk+-3.24[X=]
        x11-libs/gtk+-3.24[!X=]
        x11-libs/gtk+-3.24[X?]
        x11-libs/gtk+-3.24[!X?]

        x11-libs/gtk+-3.24[X,Y]
        x11-libs/gtk+-3.24[-X,-Y]
        x11-libs/gtk+-3.24[X=,Y=]
        x11-libs/gtk+-3.24[!X=,!Y=]
        x11-libs/gtk+-3.24[X?,Y?]
        x11-libs/gtk+-3.24[!X?,!Y?]

        x11-libs/gtk+-3.24[X,-Y]
        x11-libs/gtk+-3.24[-X,Y=]
        x11-libs/gtk+-3.24[X=,!Y=]
        x11-libs/gtk+-3.24[!X=,Y?]
        x11-libs/gtk+-3.24[X?,!Y?]
        x11-libs/gtk+-3.24[!X?,Y]

        x11-libs/gtk+-3.24[X(+),Y(-)]
        x11-libs/gtk+-3.24[X(+)=,!Y(-)=]
        x11-libs/gtk+-3.24[X(+)?,!Y(-)?]
        x11-libs/gtk+-3.24[!X(+)=,!Y(-)=]
        x11-libs/gtk+-3.24[!X(+)?,!Y(-)?]
        x11-libs/gtk+-3.24[-X(+),-Y(-)]
    """, parseAll=True)
    success &= result[0]

    result = dependency_spec.runTests("""
        (a? ( || ( x11-libs/libA1 x11-libs/libA2 ) b? ( x11-libs/libB ) ) )
        ( a?( || ( x11-libs/libA1 x11-libs/libA2 ) b? ( x11-libs/libB ) ) )
        ( a? (|| ( x11-libs/libA1 x11-libs/libA2 ) b? ( x11-libs/libB ) ) )
        ( a? ( ||( x11-libs/libA1 x11-libs/libA2 ) b? ( x11-libs/libB ) ) )
        ( a? ( || (x11-libs/libA1 x11-libs/libA2 ) b? ( x11-libs/libB ) ) )
        ( a? ( || ( x11-libs/libA1x11-libs/libA2 ) b? ( x11-libs/libB ) ) )
        ( a? ( || ( x11-libs/libA1 x11-libs/libA2) b? ( x11-libs/libB ) ) )
        ( a? ( || ( x11-libs/libA1 x11-libs/libA2 )b? ( x11-libs/libB ) ) )
        ( a? ( || ( x11-libs/libA1 x11-libs/libA2 ) b?( x11-libs/libB ) ) )
        ( a? ( || ( x11-libs/libA1 x11-libs/libA2 ) b? (x11-libs/libB ) ) )
        ( a? ( || ( x11-libs/libA1 x11-libs/libA2 ) b? ( x11-libs/libB) ) )
        ( a? ( || ( x11-libs/libA1 x11-libs/libA2 ) b? ( x11-libs/libB )) )
        ( a? ( || ( x11-libs/libA1 x11-libs/libA2 ) b? ( x11-libs/libB ) ))
    """, parseAll=True, failureTests=True)
    success &= result[0]

    if success:
        print("Success")
    else:
        print("Failure")
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
