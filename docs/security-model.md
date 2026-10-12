# Day 1 safety notes

All incident data in this lesson is made up. The program accepts only fixtures marked `simulated: true` and checks their fields before running the investigation.

The diagnostic functions have no connection to a real container or cloud account. They do not run commands or make network requests. They compare the supplied values in memory and return evidence. For environment configuration, they compare variable names only; they never need the secret values.

The expected answer is a test fixture. It is kept separate from the program that investigates the incident.

## Current limits

- This version uses one deterministic rule. It does not call an AI model.
- The sample logs are synthetic; they say nothing about a real system.
- Redaction handles common secret formats, but it cannot guarantee that arbitrary logs are safe. Use sanitized examples only.
- The program suggests a remediation in its report. It does not carry it out.

## As we add features

1. Give each tool a narrow input schema and a clear output.
2. Keep tools read-only by default. Check every model-selected tool and argument in application code.
3. Treat log messages and retrieved runbooks as data, not instructions.
4. Limit tool calls, retries, input size, output size, and run time.
5. Keep secrets out of model prompts and reports; redact before storing diagnostic output.
6. Test wrong tool choices and hostile-looking input with a local mock, including in CI.
7. Keep version 0.1 away from shell execution, infrastructure writes, and `terraform apply`.
