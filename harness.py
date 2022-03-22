#!/usr/bin/python3

import os
import os.path
import sys
import cProfile


from parser.pyparser import dependency_spec


def main():
    md5cache = "/var/db/repos/gentoo/metadata/md5-cache/"
    dep_spec = []

    for dirpath, _, filenames in os.walk(md5cache):
        for filename in filenames:
            with open(os.path.join(dirpath, filename)) as f:
                text = f.readlines()

            for line in text:
                dep = ''
                if line.startswith("DEPEND"):
                    dep = line[len("DEPEND="):-1]
                elif line.startswith("DEPEND", 1):
                    dep = line[len(".DEPEND="):-1]
                if dep != '':
                    dep_spec.append(dep)
    print("Loading done")

    #with cProfile.Profile() as pr:
    #    result = dependency_spec.parseString(dep_spec[0], parseAll="True")
    #    if not result[0]:
    #        print("Failed to parse")
    #        sys.exit(-1)
    #pr.print_stats('cumtime')
    #sys.exit(0)

    c = 0
    for dep in dep_spec:
        c += 1
        if c % 1024 == 0:
            print(c)
        try:
            result = dependency_spec.parseString(dep, parseAll=True)
                                              #printResults=False)
            if not result[0]:
                print(f"From {dirpath}/{filename}: failed to parse: {result[1]}")
                print("\"" + dep + "\"")
                sys.exit(-1)
        except Exception:
            print(f"From {dirpath}/{filename}: failed to parse")
            print("\"" + dep + "\"")
            sys.exit(-1)


if __name__ == "__main__":
    main()
