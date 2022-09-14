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
                        default="data",
                        help="path to directory with scraped data inside")
    parser.add_argument("-k", "--keywords",
                        type=str,
                        nargs="*",
                        default=["data scientist", "data engineer"],
                        help="keywords to search for (for keywords consisting of multiple words replace spaces with _)")
    args = parser.parse_args()
    return args

