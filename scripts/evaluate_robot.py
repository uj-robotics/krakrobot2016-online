#! /bin/python2.7

from optparse import OptionParser
import json

def create_parser():
    """ Configure options and return parser object """
    parser = OptionParser()
    parser.add_option(
        "-p",
        "--problem_file",
        dest="problem_file",
        default="1.json",
        help="Path to json file defining problem"
    )
    parser.add_option(
        "-r",
        "--robot_file",
        dest="robot_file",
        default="examples/python/random_search_simple.py",
        help="Path to robot binary"
    )
    parser.add_option(
        "-o",
        "--output_file",
        dest="output_file",
        default="output.json",
        help="Path to destination file"
    )
    return parser


if __name__ == "__main__":
    parser = create_parser()
    (options, args) = parser.parse_args()

    with open(options.problem_file, "r") as f:
        problem = json.loads(f.read())

