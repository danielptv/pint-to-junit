# Pint to JUnit XML

Simple converter for using the output of the Prometheus rule linter [pint](https://cloudflare.github.io/pint/) in the JUnit Jenkins plugin.
The script converts the output of the `pint lint` command to JUnit XML.

## Prerequisites

* Installation of Python 3.
* Installation of [pint](https://cloudflare.github.io/pint/#quick-start).

## How to Use

| Option             | Meaning                                                                                     |
| ------------------ | ------------------------------------------------------------------------------------------- |
| `--pint` or `-p`   | The pint output that should be converted, i.e. `"$(pint lint rule/*.yml 2>&1 >/dev/null)"`. |
| `--output` or `-o` | The output file, defaults to `results.xml`.                                                 |

You can run the script inside your Jenkins as follows:

````groovy
stage('Lint Prometheus rules with pint) {
    steps {
        // ...
        sh 'python3 pint_to_junit.py -p "$(pint lint <rules> 2>&1 >/dev/null)" -o <output.xml>'
        sh 'python3 pint_to_junit.py '<rules>' <output.xml>'
    }
}
````

Replace `<rules>` with the path to your Prometheus rules and `<output.xml>` with the path to your output XML file.
