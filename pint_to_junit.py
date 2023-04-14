# Usage: python3 pint_to_junit.py '<path to Prometheus rules>' <output file>

""" System module. """
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as xml


def clean_input(file_lines: list[str]) -> list[str]:
    """ Strip input off tabs and ANSI colorcodes. """
    regex = re.compile(r"\t|\033\[[0-9;]*m")
    clean_lines = []
    for line in file_lines:
        clean_lines.append(regex.sub("", line))
    return clean_lines


def build_testcases(case_lines: list[str]) -> xml.Element:
    """ Convert list of strings to JUnit XML testcase. """
    split = case_lines[0].split(' ')
    classname = split.pop(0)
    name = ' '.join(split)
    type_regex = re.compile(r"\(([^()]+)\)")

    testcase = xml.Element('testcase', {'name': name, 'classname': classname})
    if 'Bug' in case_lines[0]:
        failure = xml.Element('failure', {'message': name, 'type': 'failure'})
        failed_file = '\nFile: ' + classname + '\n'
        failure_type = 'Type: ' + re.search(type_regex, name).group(1) + '\n'
        description = name.split('(', maxsplit=1)[0] + '\n'
        stacktrace = 'Stacktrace: \n'
        if len(case_lines) - 1 > 0:
            for i in range(1, len(case_lines)):
                stacktrace += case_lines[i]
        failure.text = failed_file + failure_type + description + stacktrace
        testcase.append(failure)

    return testcase


def get_testcases(contents_list: list[str]) -> list[xml.Element]:
    """ Convert string input to JUnit XML testcases. """
    testcases = []
    test = []
    regex = re.compile(r"^level=*")

    for line in contents_list:
        if regex.match(line):
            continue
        if 'Bug' in line:
            if len(test) != 0:
                testcases.append(build_testcases(test))
            test = []
        test.append(line)
    return testcases


def count_type(element: xml.Element, element_type: str) -> int:
    """ Count XML child elements of a type. """
    count = 0
    for child in element:
        if child.tag == element_type:
            count += 1
        count += count_type(child, element_type)
    return count


if __name__ == '__main__':
    args = sys.argv
    if len(args) != 3:
        sys.exit("pint directory and output file must be provided.")
    print('Linting: pint lint ' + args[1])
    print('Output: ' + args[2])

    # set explicitly to avoid error
    os.environ['GOMAXPROCS'] = '1'
    # run pint
    result = subprocess.run(['pint', 'lint', args[1]], capture_output=True, text=True, check=False)
    contents = clean_input(result.stderr.split('\n'))
    cases = get_testcases(contents)
    testsuites = xml.Element('testsuites')
    testsuite = xml.Element('testsuite', {'tests': str(len(cases))})
    testsuites.append(testsuite)
    # append testcases to root element
    for case in cases:
        testsuite.append(case)
    # count errors, failures, skipped
    testsuite.set('errors', str(count_type(testsuite, 'error')))
    testsuite.set('failures', str(count_type(testsuite, 'failure')))
    testsuite.set('skipped ', str(count_type(testsuite, 'skipped')))
    # return file in junit-xml format
    tree = xml.ElementTree(testsuites)
    with open(args[2], 'wb') as file:
        tree.write(file, 'utf-8', True)
