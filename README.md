# staticdirindex

Static directory recursively create static directory indices with previews,
tagged metadata and folder information blocks.

## Usage with GitHub Pages and GitHub actions

The easiest way to deploy a site using staticdirindex is with GitHub pages
and an accompanying GitHub Action, you can find an example GitHub actions
workflow in [example-action.yml](example-action.yml)

## Usage

```
usage: staticdirindex [--sitename SITENAME] [--baseurl BASEURL] directory
```

Note that the directory indices will be generated as in-place in `directory`

### Directory header

By putting a file called `header.html` in a folder it will be included at the
start of the directory listing. The contents of `header.html` should not be a
full html document but rather an html fragment as it will be included inline.

### Ignores

By default staticdirindex will not include files or folders it uses for special
purposes in the directory listing. Note that staticdirindex will still leave
the files in place. If you want to exclude more files from the listings you can
add a `.listignore` file to the root directory with the same format as a
`.gitignore`.

### Sitemap

staticdirindex will generate a sitemap.xml in the root directory and a
robots.txt file that points to this sitemap. If the `--baseurl` parameter is
passed. (This is required to generate a [sitemap.org](https://sitemap.org)
compliant file as it requires each file location to be absolute and include
protocol)

Passing `--baseurl` will also add `<link rel="canonical">` to each directory
listing.

### schema.org json+ld

To Be Implemented, see [#6][6]

[6]: https://github.com/swantzter/staticdirindex/issues/6

### Previews

This script uses [preview-generator][preview-generator] which in terms require
several dependencies. staticdirindex fails gracefully by not including previews
for filetypes that are not supported, or where the necessary dependencies are
missing. You may have to read preview-generator's documentation to see what is
required for your system, but for ubuntu-latest the following should give you
previews for most things

```console
# apt-get install zlib1g-dev libjpeg-dev python3-pythonmagick inkscape \
  xvfb poppler-utils libfile-mimeinfo-perl qpdf libimage-exiftool-perl \
  ufraw-batch ffmpeg  libmagickwand-dev libreoffice
```

[preview-generator]: https://pypi.org/project/preview-generator/
