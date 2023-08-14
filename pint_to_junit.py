""" System module. """
import argparse
import sys
import re
import xml.etree.ElementTree as xml


class PintFinding:
    """Info about a pint finding."""

    def __init__(
        self,
        finding_type: str,
        rule_file: str,
        check: str,
        description: str,
        expression: str,
    ):
        self.finding_type = finding_type
        self.rule_file = rule_file
        self.check = check
        self.description = description
        self.expression = expression


def clean_input(file_lines: list[str]) -> list[str]:
    """Strip input off tabs and ANSI colorcodes."""
    regex = re.compile(r"\t|\033\[[0-9;]*m")
    clean_lines = []
    for line in file_lines:
        clean_lines.append(regex.sub("", line))
    return clean_lines


def build_testcase(finding: PintFinding) -> xml.Element:
    """Convert PintFinding to JUnit XML testcase."""
    testcase = xml.Element(
        "testcase", {"name": finding.description, "classname": finding.rule_file}
    )
    failure_type = "error" if finding.finding_type == "Bug" else "failure"
    failure = xml.Element(
        "failure", {"message": finding.description, "type": failure_type}
    )
    failure.text = f"""
        File: {finding.rule_file}
        Check: {finding.check}
        {finding.description}
        Expression: {finding.expression}
        """
    testcase.append(failure)
    return testcase


def get_findings(contents_list: list[str]):
    """Extract the findings from pint input."""
    findings = []
    finding = []
    filtered_contents = [
        string for string in contents_list if "level=" not in string and string != ""
    ]

    for line in filtered_contents:
        if any(keyword in line for keyword in ["Bug", "Warning", "Information"]):
            if len(finding) != 0:
                findings.append(build_finding(finding))
            finding = []
        finding.append(line)

    if len(finding) != 0:
        findings.append(build_finding(finding))

    return findings


def build_finding(content_list: list[str]):
    """Convert input for a single finding to a PintFinding object."""
    finding_type = (
        "Bug"
        if "Bug" in content_list[0]
        else ("Warning" if "Warning" in content_list[0] else "Information")
    )
    split = content_list[0].split(" ")
    rule_file = split.pop(0)
    description = " ".join(split)
    expression = next((string for string in content_list if "expr" in string), "")
    if expression:
        start_index = expression.index("expr:") + len("expr:")
        expression_trimmed = expression[start_index:]
    else:
        expression_trimmed = ""
    matches = re.search(r"\((.*?)\)", content_list[0])
    if matches:
        check = matches.group(1)
    else:
        check = ""
    return PintFinding(finding_type, rule_file, check, description, expression_trimmed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Pint to JUnit Converter",
        description="Convert pint output to JUnit XML format. ",
    )
    parser.add_argument(
        "-p", "--pint", help="Pint output that should be converted", required=True
    )
    parser.add_argument("-o", "--output", help="Output file", default="results.xml")
    args = parser.parse_args()
    print(args.pint)
    contents = clean_input(args.pint.split("\n"))
    pint_findings = get_findings(contents)

    if len(pint_findings) > 0:
        testsuites = xml.Element("testsuites")
        bug_count = sum(1 for obj in pint_findings if obj.finding_type == "Bug")
        warning_count = sum(1 for obj in pint_findings if obj.finding_type == "Warning")
        information_count = sum(
            1 for obj in pint_findings if obj.finding_type == "Information"
        )
        testsuite = xml.Element(
            "testsuite",
            {
                "tests": str(len(pint_findings)),
                "error": str(bug_count),
                "failure": str(warning_count + information_count),
                "skipped": "0",
            },
        )
        for case in pint_findings:
            testsuite.append(build_testcase(case))
        testsuites.append(testsuite)

        tree = xml.ElementTree(testsuites)
        with open(args.output, "wb") as file:
            tree.write(file, "utf-8", True)
        sys.exit(1)
