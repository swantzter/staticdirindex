# -*- coding: utf-8 -*-
# inspired by and originally adapted from: https://stackoverflow.com/questions/39048654/how-to-enable-directory-indexing-on-github-pages/40288762#40288762

import os.path
import datetime
import os
import argparse
import re
from gitignore_parser import parse_gitignore
from mako.template import Template
from mako.lookup import TemplateLookup
from preview_generator.manager import PreviewManager

EXCLUDED = ['index.html', 'header.html', '.git',
            '.gitignore', '.listignore', 'previews']


def generate(dir, rootdir, sitename, manager, ignored):

    print(f"processing:\t{dir}")
    filenames = [fname for fname in sorted(os.listdir(dir))
                 if fname not in EXCLUDED and not ignored(f"{dir}/{fname}") and os.path.isfile(f"{dir}/{fname}")]
    dirnames = [fname for fname in sorted(os.listdir(dir))
                if fname not in EXCLUDED and not ignored(f"{dir}/{fname}")]
    dirnames = [fname for fname in dirnames if fname not in filenames]
    f = open(f"{dir}/index.html", "w")
    header = open(
        f"{dir}/header.html", "r").read() if os.path.isfile(f"{dir}/header.html") else None
    # generate previews
    files = []
    for fname in filenames:
        try:
            preview = manager.get_jpeg_preview(
                f"{dir}/{fname}", height=260)
            preview = rootdir+"/"+re.sub(r'^\./?', '', preview)
        except Exception as e:
            # print(e)
            preview = None
        files.append({
            'name': fname,
            'preview': preview
        })
    print(
        Template(
            filename=f"{os.path.dirname(__file__)}/templates/index.html",
        ).render(
            dirnames=dirnames,
            files=files,
            path=re.sub('^$', '/', re.sub(r'^\.', '', dir)),
            header=header,
            now=datetime.datetime.utcnow().isoformat(),
            ROOTDIR=rootdir,
            sitename=sitename
        ),
        file=f
    )
    f.close()
    for subdir in dirnames:
        try:
            generate(f"{dir}/{subdir}", f"{rootdir}/..",
                     sitename, manager, ignored)
        except:
            pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    parser.add_argument("--sitename")
    args = parser.parse_args()

    cache_path = f"{args.directory}/previews"
    manager = PreviewManager(cache_path, create_folder=True)

    if os.path.isfile(f"{args.directory}/.listignore"):
        ignored = parse_gitignore(f"{args.directory}/.listignore")
    else:
        print("no .listignore")
        def ignored(f): return False

    generate(args.directory, args.directory, args.sitename, manager, ignored)


if __name__ == "__main__":
    main()
