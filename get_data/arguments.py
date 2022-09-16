"""
This script contains functions to capture command-line arguments for various other scripts.
"""

import argparse


def parse_directory():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory",
                        type=str,
                        default="data",
                        help="path to directory with scraped data inside")
    args = parser.parse_args()
    return args.directory


def parse_arguments():
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
    args = parser.parse_args()
    return args

