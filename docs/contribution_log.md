# Contribution log

Only what actually happened, with the real date. Commit hashes and pull request numbers are the evidence; they can be checked with `git log --all --format="%h | %an | %ad | %s" --date=short`.

| Date | Meeting / task | Person | Evidence (commit, file, recording) |
| --- | --- | --- | --- |
| 2026-11-01 | Project skeleton, requirements, configuration | Rohan Jha | `ba9c352` |
| 2026-11-19 | Data loading and weather download, Kaggle splitter, AQI functions with tests (T2), cleaning with tests (T1, T3), features with tests, build script | Rohan Jha | `51e9ed7`, `9751dcb`, `6c7971a`, `b13e062`, `483dfcb`, `bab2345`, `7a4981e`, `b9227a0`, `95cfb66`; merged in PR #1 (`95d4476`) |
| 2026-11-19 | Contribution log template and dashboard wording (`app/text.py`) | Rohan Jha | `50dba82`, `0835666`; merged in PR #2 (`65ed9db`) |
| 2026-11-21 | Data notes, baseline models (persistence, climatology, ridge), evaluation code, evaluation tests (T4) | Udbhav Saxena | `d78646c`, `4978753`, `afc8b18`, `09990cc` |
| 2026-11-21 | Team call with all three members covering how to review PRs #1 and #2 | Rohan Jha, Udbhav Saxena, Manan Jain | Call (no file) |
| 2026-11-22 | Rohan guided Udbhav through reviewing and approving PR #1 and PR #2, and through creating a pull request | Rohan Jha, Udbhav Saxena | Reviews on PR #1 and PR #2 (GitHub) |
| 2026-11-22 | Merged PR #1 and PR #2 into `main`; Udbhav merged `main` into his branch | Rohan Jha, Udbhav Saxena | `95d4476`, `65ed9db`, `6ba7dd9` |
| 2026-11-22 | Call covering Udbhav's training run on the real data; training script committed | Rohan Jha, Udbhav Saxena | `8ca56a7`; call (no file) |
| 2026-11-22 | Dashboard core: shared helpers, status panel, trends panel, pollution-weather panel | Rohan Jha | `a4f70d0`, `13c35ed`, `6a981d3`, `5c66339`; PR #3 (`f291d82`) |
| 2026-11-22 | Forecast panel and About and limits panel | Rohan Jha | `1fccf0e`, `13780dc`; PR #4 (`53d5a1d`) |
| 2026-11-22 | Dashboard shell with station and date selectors | Rohan Jha | `d1c3000`; PR #5 (`2e3bdfa`) |
| 2026-11-22 | Data sources and licence notes, baseline results (`metrics.csv`); reviewed and merged by Rohan | Udbhav Saxena | `04f276d`, `5f714f5`; PR #6 (`30986c9`) |
| 2026-11-22 | Test log with real results (19 tests passed) and dashboard screenshots | Rohan Jha | `cca645d`; PR #7 (`e2025b4`) |
| 2026-11-23 | README with setup, run steps and data sources | Rohan Jha | `8d3c85c`, `1bca5ab`; PR #8 (`3e01b4b`) |
| 2026-11-23 | Technical synopsis | Rohan Jha | `1dfc47f`; PR #9 (`13eb078`) |

## Tools used

Claude (an AI assistant by Anthropic) was used for step-by-step guidance on Git and GitHub, code review, and drafting parts of the documentation. The team ran the code and tests, checked the results against the real files, and is responsible for the submitted work.
