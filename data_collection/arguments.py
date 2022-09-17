"""
This script contains functions to capture command-line arguments for various other scripts.
"""

import argparse


def parse_webscraper():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory",
                        type=str,
                        required=True,
                        # default="data",
                        help="path to directory with scraped data inside")
    parser.add_argument("-k", "--keywords",
                        type=str,
                        nargs="*",
                        default=["data scientist", "data engineer"],
                        help="keywords to search for (to specifiy keywords consisting of multiple words use '_' instead"
                             " of spaces)")
    parser.add_argument("-s", "--salary",
                        action="store_true",
                        help="whether additional salary information should be scraped, which is only visible when"
                             " logged in (requires a Stepstone account)")
    args = parser.parse_args()
    return args


def parse_preprocessing():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory",
                        type=str,
                        default="data",
                        help="path to directory with scraped data inside")
    parser.add_argument("-g", "--geo_data",
                        action="store_true",
                        help="whether additional geographic information should be requested from the Positionstack API"
                             " (requires a Positionstack account)")
    args = parser.parse_args()
    return args


def parse_positionstack():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory",
                        type=str,
                        default="data",
                        help="path to directory with scraped data inside")
    args = parser.parse_args()
    return args

