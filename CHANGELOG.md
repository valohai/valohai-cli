### Changelog

#### [v0.30.1](https://github.com/valohai/valohai-cli/compare/v0.30.0...v0.30.1)

> 10 Apr 2025

- Include unfinished job count with `--queue`

#### [v0.30.0](https://github.com/valohai/valohai-cli/compare/v0.29.0...v0.30.0)

> 5 March 2025

- Support overriding environments for pipeline nodes [`#326`](https://github.com/valohai/valohai-cli/pull/326)

#### [v0.29.0](https://github.com/valohai/valohai-cli/compare/v0.28.0...v0.29.0)

> 28 Feb 2025

- Add priority flag to `vh exec` command [`#319`](https://github.com/valohai/valohai-cli/pull/319), [`#321`](https://github.com/valohai/valohai-cli/pull/321)
- Support the `time-limit` setting in `valohai.yaml`  [`#324`](https://github.com/valohai/valohai-cli/pull/324)

#### [v0.28.0](https://github.com/valohai/valohai-cli/compare/v0.27.0...v0.28.0)

> 4 November 2024

- Dependency upgrades & minor CI renovation [`#318`](https://github.com/valohai/valohai-cli/pull/318)

#### [v0.27.0](https://github.com/valohai/valohai-cli/compare/v0.26.0...v0.27.0)

> 12 September 2024

- Add SSH command for executions [`#314`](https://github.com/valohai/valohai-cli/pull/314)
- Option to disable git packaging for adhoc runs [`#313`](https://github.com/valohai/valohai-cli/pull/313)
- Support list parameters for pipelines [`#311`](https://github.com/valohai/valohai-cli/pull/311)
- Smoother token login flow [`#310`](https://github.com/valohai/valohai-cli/pull/310)
- Add command line parameter for runtime config preset [`#305`](https://github.com/valohai/valohai-cli/pull/305)
- Refactorings & upgrades

#### [v0.26.0](https://github.com/valohai/valohai-cli/compare/v0.25.0...v0.26.0)

> 3 January 2024

- This version is the first to require Python 3.8.
- Improved Kubernetes support.
- Improved help text and documentation.

#### [v0.25.0](https://github.com/valohai/valohai-cli/compare/v0.24.0...v0.25.0)

> 11 September 2023

- Add commit_identifier in pipeline's run [`#287`](https://github.com/valohai/valohai-cli/pull/287)
- Pipeline parameters overriding [`#285`](https://github.com/valohai/valohai-cli/pull/285)
- Honour --yaml flag to parse configuration in vh pipeline run --adhoc [`#281`](https://github.com/valohai/valohai-cli/pull/281)
- Add missing slash into authtoken url [`#278`](https://github.com/valohai/valohai-cli/pull/278)
- Add Override support for pipeline parameters [`89d83c5`](https://github.com/valohai/valohai-cli/commit/89d83c55ea77e342078d8c9ba1bb41902b749ee5)
- Use --yaml flag to parse current configuration in pipeline run [`603934b`](https://github.com/valohai/valohai-cli/commit/603934b833c2db1bb3e06708f5656dc184e6698b)

#### [v0.24.0](https://github.com/valohai/valohai-cli/compare/v0.23.0...v0.24.0)

> 22 February 2023

- Add option to list only my executions [`#275`](https://github.com/valohai/valohai-cli/pull/275)
- Drop support for EOL Python 3.6 [`df1b8b1`](https://github.com/valohai/valohai-cli/commit/df1b8b1dc66cde5cae8807899b09e17f6a7fc9d7)

#### [v0.23.0](https://github.com/valohai/valohai-cli/compare/v0.22.2...v0.23.0)

> 7 February 2023

- Fix exec remote debug API call correct format [`#273`](https://github.com/valohai/valohai-cli/pull/273)
- Lint with pre-commit + ruff [`#272`](https://github.com/valohai/valohai-cli/pull/272)
- List only deleted executions [`#267`](https://github.com/valohai/valohai-cli/pull/267)

#### [v0.22.2](https://github.com/valohai/valohai-cli/compare/v0.22.1...v0.22.2)

> 10 November 2022

- ♻️✅ Conflate how git is managed in tests [`#247`](https://github.com/valohai/valohai-cli/pull/247)
- CI: publish to PyPI too [`#248`](https://github.com/valohai/valohai-cli/pull/248)


#### [v0.22.1](https://github.com/valohai/valohai-cli/compare/v0.22.0...v0.22.1)

> 9 November 2022 (not released)

- 🐛 Allow partial matches when resolving commits [`#243`](https://github.com/valohai/valohai-cli/pull/243)
- 🧑‍💻🔨 Improve developer experience [`#242`](https://github.com/valohai/valohai-cli/pull/242)

#### [v0.22.0](https://github.com/valohai/valohai-cli/compare/v0.21.0...v0.22.0)

> 31 October 2022

- Add description values to package metadata [`#203`](https://github.com/valohai/valohai-cli/pull/203)
- Allow selecting an owner for the new project [`#219`](https://github.com/valohai/valohai-cli/pull/219)
- Allow specifying --ca-file during login (or in settings) [`#234`](https://github.com/valohai/valohai-cli/pull/234)
- Allow tagging pipelines [`#209`](https://github.com/valohai/valohai-cli/issues/209)
- Ensure valohai-utils entry in requirements is prepended by newline [`#240`](https://github.com/valohai/valohai-cli/pull/240)
- Execution run command: handle multiple-styled parameters [`#212`](https://github.com/valohai/valohai-cli/pull/212)
- Spot restart [`#210`](https://github.com/valohai/valohai-cli/pull/210)
- Validate commit in respect to the active project [`#218`](https://github.com/valohai/valohai-cli/pull/218)

#### [v0.21.0](https://github.com/valohai/valohai-cli/compare/v0.20.1...v0.21.0)

> 23 June 2022

- Add data and alias command to fetch Datums and Datum Aliases [`#200`](https://github.com/valohai/valohai-cli/pull/200)
- Keep create_adhoc_commit_from_tarball in tact [`#202`](https://github.com/valohai/valohai-cli/pull/202)

#### [v0.20.1](https://github.com/valohai/valohai-cli/compare/v0.20.0...v0.20.1)

> 20 June 2022

- Default to valohai.yaml properly when path in project data is None [`#201`](https://github.com/valohai/valohai-cli/pull/201)

#### [v0.20.0](https://github.com/valohai/valohai-cli/compare/v0.19.0...v0.20.0)

> 16 June 2022

- Allow creating adhoc commits with a nonstandard yaml path [`#192`](https://github.com/valohai/valohai-cli/pull/192)

#### [v0.19.0](https://github.com/valohai/valohai-cli/compare/v0.18.0...v0.19.0)

> 20 April 2022

- Fix formatting for *SV output [`b52cd4f`](https://github.com/valohai/valohai-cli/commit/b52cd4f3e26eb03c5338cf061fb35e1940ecc733)
- Upgrade to gitignorant 0.2.0, use check_path_match [`#191`](https://github.com/valohai/valohai-cli/pull/191)
- Use images.v2.yaml instead of legacy images.yaml [`#190`](https://github.com/valohai/valohai-cli/pull/190)

#### [v0.18.0](https://github.com/valohai/valohai-cli/compare/v0.17.0...v0.18.0)

> 20 January 2022

- Add transient setting `api_user_agent_prefix` [`#180`](https://github.com/valohai/valohai-cli/pull/180)
- Use valohai-yaml 0.21+ pipeline conversion code [`ffb4e1c`](https://github.com/valohai/valohai-cli/commit/ffb4e1c8eb93e45c20f294ed0f6fe3deae53b6f9)

#### [v0.17.0](https://github.com/valohai/valohai-cli/compare/v0.16.0...v0.17.0)

> 3 November 2021

- Add remote debug flags [`#179`](https://github.com/valohai/valohai-cli/pull/179)

#### [v0.16.0](https://github.com/valohai/valohai-cli/compare/v0.15.1...v0.16.0)

> 22 October 2021

- Adhoc .vhignore support [`#171`](https://github.com/valohai/valohai-cli/pull/171)
- Adhoc pipeline runs [`#176`](https://github.com/valohai/valohai-cli/pull/176)
- Allow disabling SSL verification when logging in [`#167`](https://github.com/valohai/valohai-cli/pull/167)
- Have a more consistent CLI option for create new project [`#175`](https://github.com/valohai/valohai-cli/pull/175)
- Make `vh exec stop latest` work [`#166`](https://github.com/valohai/valohai-cli/pull/166)
- Make optional inputs without default work for pipeline runs [`#169`](https://github.com/valohai/valohai-cli/pull/169)
- Python 3.10 compatibility [`#173`](https://github.com/valohai/valohai-cli/pull/173)
- Ship py.typed [`#177`](https://github.com/valohai/valohai-cli/pull/177)
