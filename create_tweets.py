import json
import os
from collections import namedtuple
from pathlib import Path
from textwrap import dedent

import tweepy


osenv = os.environ

EpsPair = namedtuple("EpsPair", ["new", "old"])


NEW_PKG_MSG = dedent(
    """\
    *** New Package ***

    {pkg} v{version}

    {summary}

    https://pypi.org/project/{pkg}
    """
)

UPD_PKG_MSG = dedent(
    """\
    *** Updated Package ***

    {pkg} v{version}

    {summary}

    https://pypi.org/project/{pkg}
    """
)


def get_eps():
    eps_rep = json.loads(Path("data", "eps_rep.json").read_text())
    eps_rep_old = json.loads(Path("data", "eps_rep.json.old").read_text())
    eps_ext = json.loads(Path("data", "eps_ext.json").read_text())
    eps_ext_old = json.loads(Path("data", "eps_ext.json.old").read_text())

    return EpsPair(eps_rep, eps_rep_old), EpsPair(eps_ext, eps_ext_old)


def get_api():
    auth = tweepy.OAuthHandler(osenv["F8_TWITTER_KEY"], osenv["F8_TWITTER_SECRET_KEY"])
    auth.set_access_token(osenv["F8_TWITTER_TOKEN"], osenv["F8_TWITTER_SECRET_TOKEN"])

    return tweepy.API(auth)


def tweet_new_package(api, *, pkg, version, summary):
    api.update_status(NEW_PKG_MSG.format(pkg=pkg, version=version, summary=summary))


def tweet_upd_package(api, *, pkg, version, summary):
    api.update_status(UPD_PKG_MSG.format(pkg=pkg, version=version, summary=summary))


def set_new_packages(eps_pair):
    return {pkg for pkg in eps_pair.new if pkg not in eps_pair.old}


def set_upd_packages(eps_pair):
    return {
        pkg
        for pkg in eps_pair.old
        if pkg in eps_pair.new
        and (eps_pair.old[pkg]["version"] != eps_pair.new[pkg]["version"])
    }


def main():
    api = get_api()

    eps_pair_rep, eps_pair_ext = get_eps()

    new_pkgs = set.union(*map(set_new_packages, (eps_pair_rep, eps_pair_ext)))
    upd_pkgs = set.union(*map(set_upd_packages, (eps_pair_rep, eps_pair_ext)))

    for pkg in new_pkgs:
        print(f"**** Tweeting new package: {pkg} ****")
        pkg_data = eps_pair_rep.new.get(pkg, eps_pair_ext.new[pkg])
        tweet_new_package(
            api, pkg=pkg, version=pkg_data["version"], summary=pkg_data["summary"]
        )

    for pkg in upd_pkgs:
        print(f"**** Tweeting updated package: {pkg} ****")
        pkg_data = eps_pair_rep.new.get(pkg, eps_pair_ext.new[pkg])
        tweet_upd_package(
            api, pkg=pkg, version=pkg_data["version"], summary=pkg_data["summary"]
        )


if __name__ == "__main__":
    main()
