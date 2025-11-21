Feature: Website Scan
  Scenario: Run scan on a known site
    Given I have a target URL "https://example.com"
    When I run the scanner once
    Then a report file should be created
