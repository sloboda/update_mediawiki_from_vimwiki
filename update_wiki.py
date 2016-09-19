#!/usr/bin/env python

"""update_wiki  Update a mediawiki site

This script grabs mediawiki login credentials from a configuration file,
 scans a directory to build a list of files ending in the suffix ".wiki"
For each file, the script updates the mediawiki page with the wiki file.

This is a one way update.
Details go from the vimwiki file to the mediawiki.
There's no pull from the mediawiki back to vimwiki.  Yet.

Future planned edits:
1) use mwclient Page revisions feature along with a filesystem feature
 to find and compare timestamps in UTC and only update pages that are
 newer on the filesystem.
http://mwclient.readthedocs.io/en/latest/reference/page.html#mwclient.page.Page

2) compare source in bytes and dest in bytes.
If they are the same, don't copy.
"""

import ConfigParser
import mwclient
import os
import re


CONFIGFILE = '/home/david/.wiki.config'

def get_config_value(term):
    """ pull a configuration term from a file

    File contains credentials for logging in,
    contains path to vimwiki,
    contains URL for mediawiki,
    describes file name for index page on vimwiki,
    describes file name for index page on mediawiki

    ### Begin sample config file: ###
    [publicwiki]
    username: accountWithWritePrivileges
    password: secret
    wikiname: localhost
    wikibasepath: /mywiki/
    wikifilepath: /home/user/vimwiki_directories/PublicWiki
    vimwikiindexname: index
    mediawikiindexname: Main Page
    ### End sample config file  ###
    """
    config = ConfigParser.ConfigParser()
    config.read(CONFIGFILE)
    returned_term = config.get('publicwiki', term)
    return returned_term


def replace_page(pagename, contents):
    """ replace the contents of a page"""
    wikiname = get_config_value("wikiname")
    wikibasepath = get_config_value("wikibasepath")
    username = get_config_value("username")
    password = get_config_value("password")
    site = mwclient.Site(('http', wikiname),
                         wikibasepath,
                         force_login=True)
    site.login(username, password)
    page = site.Pages[pagename]
    page.save(contents, summary='Pythonic update from vimwiki')


def pull_page(myfullfile, mypagename):
    """ replace page on wiki with file contents """
    pagename = mypagename
    with open(myfullfile, 'r') as myfile:
        contents = ""
        raw_data = myfile.read()
        # replace heading one with empty string
        # mediawiki provides heading one from file name
        heading = (r'^= .* =$')
        patr = re.compile(heading)
        for line in raw_data.split('\n'):
            newline = ""
            if patr.match(line):
                newline = patr.sub('', line)
            else:
                newline = line
            contents = contents + newline + '\n'
    replace_page(pagename, contents)
#    print "I replaced %s" % (pagename)


def main():
    """ where it all gets done"""
    vimwikifilepath = get_config_value("vimwikifilepath")
    vimwikiindexname = get_config_value("vimwikiindexname")
    mediawikiindexname = get_config_value("mediawikiindexname")
    myterm = (r'.wiki$')
    file_list = []
    for filenames in os.walk(vimwikifilepath):
        for myfile in filenames[2]:
            file_list.append(myfile)
        break
    for myfile in file_list:
        if myfile.endswith(".wiki"):
            pat = re.compile(myterm)
            mfs = pat.sub('', myfile)
            myfullfile = vimwikifilepath + "/" + myfile
            # replace filename "index" with mediawiki required "Main Page"
            if mfs == vimwikiindexname:
                mfs = mediawikiindexname
            pull_page(myfullfile, mfs)


if __name__ == "__main__":
    main()

