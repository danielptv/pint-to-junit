# Pint to JUnit XML

Simple converter for using the output of the Prometheus rule linter [pint](https://cloudflare.github.io/pint/) in the JUnit Jenkins plugin.

## Prerequisites

* Installation of Python 3.
* Installation of [pint](https://cloudflare.github.io/pint/#quick-start).

## How To Use

You can run the script inside your Jenkins as follows:
````
stage('Lint Prometheus rules with pint) {
    steps {
        // ...
        sh 'python3 pint_to_junit.py '<rules>' <output.xml>'
    }
}
````
Replace ***\<rules>*** with the path to your Prometheus rules and ***\<output file>*** with the path to your output XML file.

**Important:** If you use pattern matching to lint multiple rule files at once make sure to quote the expression with single quotes: **'**\<rules>**'**.