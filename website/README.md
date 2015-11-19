# Publishing the website

## Get a local copy of the repository

If you don't already have a copy of the repository, clone it:

* `git clone git@github.com:whdc/saphon.git`

This creates a `saphon` directory that contains the entire repository.  If you have this directory already, update it: `cd` to it and run:

* `git pull -r`

If this doesn't produce expected results, perhaps it's because you're not on the master branch.  To check which branch you're on, run:

* `git status`

And to switch to master, run:

* `git checkout master`

Then try pulling again.

## Set PYTHONPATH

The website is built using Python 3 code in the `python` subdirectory.  Before running Python 3, you have to set the environment variable `PYTHONPATH` to point there.  From within the `python` subdirectory, run:

* `pwd`
  
This tells you the path to add to `PYTHONPATH`.  (When I do that, I get `/Users/wchang/git/saphon/python`.)  Add it to `PYTHONPATH` by running, mutatis mutandis:

* `export PYTHONPATH=$PYTHONPATH:/Users/wchang/git/saphon/python`

You can make this happen automatically by putting this line in `~/.bash_profile`.  You can check `PYTHONPATH` by running:

* `echo $PYTHONPATH`

## Building the website locally

The `website` subdirectory contains the makefile for building and publishing the website.  Take a look at `website/Makefile` in an editor to familiarize yourself with what it does.

The command `html` creates the subdirectory `html`, which is used as scratch space for holding the website files before they are published.  The invocation of `python3` creates all the generated files, and the invocation of `rsync` copies in all the pre-fab files from the `intact` subdirectory.  Since the `html` subdirectory is scratch space, take care never to enter its contents into the repository. (And if you accidentally do, delete them.)

To build the website, first delete the old `html` subdirectory by running:

* `make clean`

Then run:

* `make html`

## Publishing

To see what the files in `html` look like without actually publishing, you can publish to an alternate set of URLs.  Run:

* `make publish-hidden`

This will publish to `http://linguistics.berkeley.edu/~saphon/hidden`.  If you are happy with what you see, run:

* `make publish-main`
