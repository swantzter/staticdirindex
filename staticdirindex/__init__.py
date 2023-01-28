# -*- coding: utf-8 -*-
# inspired by and originally adapted from: https://stackoverflow.com/questions/39048654/how-to-enable-directory-indexing-on-github-pages/40288762#40288762

import os.path
import datetime
import os
import argparse
import re
from urllib.parse import quote as urlquote
from gitignore_parser import parse_gitignore
from mako.template import Template
from mako.lookup import TemplateLookup
from preview_generator.manager import PreviewManager

__version__ = '1.11'

EXCLUDED = ['index.html', 'header.html', '.git',
            '.gitignore', '.listignore', 'previews',
            'robots.txt', 'sitemap.xml']


def generate(dir, rootdir, sitename, url, manager, ignored, sitemap):
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
        except:
            # print(e)
            preview = None
        files.append({
            'name': fname,
            'url': f"{url}/{urlquote(fname, safe='')}",
            'preview': preview
        })
        sitemap.append({
            'url': f"{url}/{urlquote(fname, safe='')}",
            'changefreq': 'never'
        })

    # generate folder metadata
    directories = []
    for dirname in dirnames:
        directories.append({
            'name': dirname,
            'url': f"{url}/{urlquote(dirname, safe='')}",
        })
        sitemap.append({
            # GH pages appends a / to the end of the url when serving index.html,
            # sitemap.org'sschema requires such / to be present in <loc> if it's
            # required
            'url': f"{url}/{urlquote(dirname, safe='')}/",
            'changefreq': 'monthly'
        })

    print(
        Template(
            filename=f"{os.path.dirname(__file__)}/templates/index.html",
        ).render(
            directories=directories,
            files=files,
            canonical=url if url.startswith('http') else None,
            path=re.sub('^$', '/', re.sub(r'^\.', '', dir)),
            header=header,
            now=datetime.datetime.utcnow().isoformat(),
            ROOTDIR=rootdir,
            sitename=sitename,
            version=__version__
        ),
        file=f
    )

    f.close()

    for subdir in dirnames:
        try:
            generate(
                dir=f"{dir}/{subdir}",
                rootdir=f"{rootdir}/..",
                sitename=sitename,
                url=f"{url}/{urlquote(subdir, safe='')}",
                manager=manager,
                ignored=ignored,
                sitemap=sitemap
            )
        except:
            pass

    if dir == rootdir and url.startswith('http'):
        f = open(f"{dir}/sitemap.xml", "w")
        print(
            Template(
                filename=f"{os.path.dirname(__file__)}/templates/sitemap.xml",
            ).render(
                paths=sitemap
            ),
            file=f
        )
        f.close()

        f = open(f"{dir}/robots.txt", "r+")
        contents = f.read()
        if not f"Sitemap: {url}/sitemap.xml" in contents:
            print(f"Sitemap: {url}/sitemap.xml", file=f)
        f.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="path to the directory that will be processed")
    parser.add_argument("--sitename", help="Name of the site, for <title> and such")
    parser.add_argument("--baseurl", help="Base URL for where the site will be published, used for sitemap and such. ex. https://example.com")
    args = parser.parse_args()

    cache_path = f"{args.directory}/previews"
    manager = PreviewManager(cache_path, create_folder=True)
    sitemap = []

    if os.path.isfile(f"{args.directory}/.listignore"):
        ignored = parse_gitignore(f"{args.directory}/.listignore")
    else:
        print("no .listignore")
        def ignored(f): return False

    generate(
        dir=args.directory,
        rootdir=args.directory,
        sitename=args.sitename,
        url=args.baseurl if args.baseurl is not None else '',
        manager=manager,
        ignored=ignored,
        sitemap=sitemap
    )


if __name__ == "__main__":
    main()
