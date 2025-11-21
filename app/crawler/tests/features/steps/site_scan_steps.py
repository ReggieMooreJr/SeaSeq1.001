from behave import given, when, then
import os
import subprocess

@given('I have a target URL "{url}"')
def step_given_url(context, url):
    context.url = url

@when('I run the scanner once')
def step_run_scan(context):
    cmd = ["bash", "run-scan.sh", "once", context.url]
    context.result = subprocess.run(cmd, capture_output=True, text=True)
    context.output = context.result.stdout

@then('a report file should be created')
def step_check_report(context):
    assert os.path.exists("reports/report.html"), "Report file not found"
