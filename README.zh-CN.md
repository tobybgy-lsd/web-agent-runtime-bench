# Agent Failure Doctor

- 当前里程碑：Agent Failure Doctor v3.2 Auto Collector P98 Gate
- 上一个 P98 稳定线：Agent Failure Doctor v3.1.0 P98 Master Gate
- 上一个 P95 稳定线：Agent Failure Doctor v2.4.1 P95 Alignment & Missing Tracks Pack

Agent Failure Doctor 是一个本地优先的 AI 自动化失败诊断工具，面向 AI Browser Agent、Playwright、RPA、爬虫自动化和数据采集脚本调试。

## 一键本地采集与诊断

```powershell
failure-doctor collect --project . --preset auto --out .\failure_doctor_auto_report --auto-diagnose --auto-handoff --auto-sanitize
failure-doctor watch --project . --out .\failure_reports --once --auto-diagnose
failure-doctor run --capture -- python .\examples\mock_script_fails.py
```

非技术 Windows 用户可以双击 `scripts/windows/Start-FailureDoctor-Diagnosis.bat`，也可以把失败项目文件夹拖到这个 BAT 上。

`collect` 只扫描你授权的项目文件夹，不扫描整台电脑，不读取浏览器用户资料、凭据库、SSH key、`.git`、`node_modules` 或虚拟环境目录；不会上传任何文件。对外分享前只查看并分享 `sanitized_failure_pack/`。

**Core lifecycle:** `failure-doctor collect` / `failure-doctor diagnose` / `failure-doctor batch` -> `failure-doctor plan` -> `failure-doctor handoff` / `failure-doctor propose-patch` -> `failure-doctor verify` -> `failure-doctor sanitize`

**P98 gate:** `knowledge base -> coverage matrix -> trace/cross-framework/training/composite/handoff/batch/sanitize/auto-collector -> master gate`

**Advanced commands:**

```powershell
failure-doctor handoff .\report --target codex --out .\ai_handoff
failure-doctor propose-patch --repo . --report .\report --out .\patch_plan
failure-doctor batch .\runs --out .\batch_report
```

[English documentation](README.md)

Agent Failure Doctor 鏄竴涓湰鍦颁紭鍏堢殑 AI 鑷姩鍖栧け璐ヨ瘖鏂伐鍏凤紝闈㈠悜 AI Browser Agent銆丳laywright銆丷PA銆佺埇铏嚜鍔ㄥ寲鍜屾暟鎹噰闆嗚剼鏈皟璇曘€?
**杈撳叆锛?* `trace.zip` / `error.log` / `console.txt` / `network.json` / 鎴浘 metadata / `user_description.txt`

**杈撳嚭锛?* 璇婃柇缁撹銆佽瘉鎹€佷笅涓€姝ャ€佷慨澶嶅缓璁€丟itHub issue 鑽夌銆丆odex 淇 Prompt銆?
## 蹇€熷紑濮?
```powershell
git clone https://github.com/tobybgy-lsd/web-agent-runtime-bench.git
cd web-agent-runtime-bench
python -m pip install -e .
failure-doctor diagnose .\examples\failed_runs\proxy_network_error --out .\report
```

## 杈撳嚭鏂囦欢

```text
report/
|-- diagnosis.json
|-- diagnosis.md
|-- evidence.json
|-- input_summary.json
|-- issue_draft.md
|-- repair_suggestions.md
|-- codex_fix_prompt.md
`-- failure_doctor_report.zip
```

## 楠岃瘉淇鏄惁鐪熺殑鎴愬姛

```powershell
failure-doctor diagnose .\failed_run --out .\report
failure-doctor plan .\report --out .\fix_plan
failure-doctor verify --before .\failed_run --after .\rerun_after_fix --out .\verification_report
```

`verify` 浼氬姣?before/after 璇佹嵁锛屽垽鏂師澶辫触鏄惁宸茶В鍐炽€佹槸鍚︽湭瑙ｅ喅銆佹槸鍚﹀彉鎴愬彟涓€涓け璐ワ紝鎴栬瘉鎹笉瓒炽€?
## 澶嶅悎鏁呴殰璇婃柇

Agent Failure Doctor 鐜板湪鍙互鍦ㄥ鏉傚け璐ラ噷鍚屾椂杈撳嚭涓绘晠闅溿€佹鏁呴殰銆侀樆鏂晠闅溿€佷笅娓告晠闅溿€佽瘉鎹浘鍜屼慨澶嶉『搴忋€傛棫瀛楁 `technical_category` / `subtype` / `confidence` 浠嶇劧淇濈暀锛屾柟渚挎棫鑴氭湰缁х画浣跨敤銆?
澶嶅悎璇婃柇浠嶇劧鏄湰鍦般€佺‘瀹氭€с€佸彲鍥炲綊鐨勮鍒欏紩鎿庯紱涓嶈皟鐢ㄥ閮?AI锛屼笉涓婁紶 artifact锛屼篃涓嶆彁渚涢獙璇佺爜缁曡繃銆侀鎺ц閬裤€佹寚绾逛吉閫犮€佸姩鎬佺鍚嶇牬瑙ｆ垨鏈巿鏉冮噰闆嗗缓璁€?
## v0.9 楠岃瘉鐘舵€?
- 131 鏉?source ledger 璁板綍锛屽苟鍖哄垎鐪熷疄鍏紑 issue銆佸畼鏂规枃妗ｈ涓鸿竟鐣屻€乸ublic-inspired sanitized 璁板綍
- 50 鏉″彲杩芥函鐪熷疄鍏紑 issue 璁板綍
- 30 涓敱 Playwright 鍘熺敓鐢熸垚鐨?`trace.zip` fixtures
- 鐪熷疄 trace 楠岃瘉锛?0/30 鍚堢悊鍒嗙被
- 鐪熷疄 trace 楠岃瘉锛?0/30 绮剧‘ subtype
- 62 鏉?external public reference seed
- 20 鏉?external public reference held-out 璁板綍
- external public reference 楠岃瘉锛?0/20 鍚堢悊鍒嗙被锛?0/20 鍙墽琛屼笅涓€姝?- 12 缁?resolution validation before/after 妗堜緥
- resolution validation锛?2/12 鐘舵€佸垽鏂纭?- external held-out 楠岃瘉锛?0 鏉″叕寮€鏉ユ簮璁板綍锛?/10 鍚堢悊鍒嗙被锛?0/10 鍙墽琛屼笅涓€姝?- 鐢熸垚鎶ュ憡鍜?Prompt 鐨?forbidden output 涓?0

璇﹁ [validation/dashboard.md](validation/dashboard.md)銆乕docs/VALIDATION_REPORT.md](docs/VALIDATION_REPORT.md) 鍜?[docs/EXTERNAL_DATA_SOURCES.md](docs/EXTERNAL_DATA_SOURCES.md)銆?
## 澶嶇幇鐪熷疄 Trace 楠岃瘉

```powershell
python -m pip install -e .[trace-gen]
python -m tools.real_trace_generation.generate_real_trace_fixtures --out .\examples\realistic_playwright_traces --count 30 --clean
python -m tools.validation.run_real_trace_validation
python -m tools.validation.run_external_public_reference_validation
python -m tools.validation.run_resolution_validation
python scripts\validate_external_heldout.py
```

## 瀹夊叏杈圭晫

鏈」鐩彧鍋氭湰鍦般€佽劚鏁忔潗鏂欒瘖鏂紝涓嶄笂浼?trace銆佹棩蹇椼€乧ookie銆乼oken銆佺綉缁滃寘鎴栨埅鍥俱€?
鏈」鐩笉鏄細

- 鎸戞垬椤甸潰鑷姩澶勭悊宸ュ叿
- 璁块棶鎺у埗瑙勯伩宸ュ叿
- 鍑嵁鎻愬彇宸ュ叿
- 鐪熷疄骞冲彴閲囬泦鍣?- 鏈巿鏉冮噰闆嗗伐鍏?
濡傛灉鐤戜技閬囧埌骞冲彴璁块棶闄愬埗鎴栭鎺ц竟鐣岋紝宸ュ叿鍙粰鍑鸿瘑鍒€佸垎娴佸拰鍚堣寤鸿锛屼緥濡備娇鐢ㄥ畼鏂?API銆佺‘璁ゆ巿鏉冦€侀檷浣庤闂噺銆佽仈绯诲钩鍙版垨鍋滄鏈巿鏉冮噰闆嗐€?
## 璐＄尞澶辫触妗堜緥

浣犱笉闇€瑕佸啓浠ｇ爜銆傛渶鏈変环鍊肩殑璐＄尞鏄彁浜や竴涓劚鏁忓け璐ユ渚嬨€?
璇锋彁渚涳細

- 浣跨敤鐨勫伐鍏凤細Playwright / browser-use / Scrapy / requests / Codex / RPA / other
- 杈撳叆绫诲瀷锛歵race.zip / error.log / console.txt / network.json / screenshot / description
- 澶辫触鐜拌薄
- 棰勬湡琛屼负
- 瀹為檯琛屼负
- 鑴辨晱閿欒鎽樿
- 鏄惁鍙互鍙樻垚鍏紑娴嬭瘯妗堜緥

涓嶈鎻愪氦瀵嗙爜銆乧ookie銆乼oken銆乤uthorization header銆丄PI key銆佺鏈?URL銆乸rivate data銆佷釜浜烘暟鎹垨瀹㈡埛鏁版嵁銆?
娆㈣繋鎻愪氦鑴辨晱鍚庣殑 `error.log`銆乣trace.zip`銆乣console.txt`銆乣network.json`銆佹埅鍥?metadata 鎴?`user_description.txt`銆傚鏋滀綘鍏佽锛屾渚嬩細鑾峰緱 `EXT-YYYY-NNNN` 缂栧彿锛屽苟鍦ㄤ笉鍏堣皟瑙勫垯鐨勬儏鍐典笅鐢ㄥ綋鍓嶅彂甯冪増鏈?first-run 涓€娆★紝缁撴灉杩涘叆 [澶栭儴楠岃瘉浠〃鐩榏(validation/external_validation_dashboard.md)銆?
妯℃澘鍜屼綔鑰呰嚜宸辩敓鎴愮殑绀轰緥涓嶈鍏ュ閮ㄩ獙璇佹寚鏍囥€傝缁嗘祦绋嬭 [docs/external_validation_protocol.md](docs/external_validation_protocol.md) 鍜?[docs/REAL_TRACE_CONTRIBUTION_GUIDE.md](docs/REAL_TRACE_CONTRIBUTION_GUIDE.md)銆?
## Applied Scenario Demos

Local-only mock demos show how Agent Failure Doctor diagnoses failures in hot product collection, live commerce monitoring, ecommerce listing automation, authorized content publishing workflow, GUI/RPA data bridge, and ERP-to-ecommerce sync.

```powershell
python -m tools.validation.run_applied_scenario_validation
```

These demos are failure diagnosis packs, not production business systems.

Current result: 18/18 reasonable classifications, 18/18 valid fix plans, 18/18 correct verification statuses, 0 forbidden outputs.

## Integration Pack

Agent Failure Doctor v1.2 adds local integration adapters:

```powershell
failure-doctor collect-playwright .\examples\mock_playwright_test_results --out .\tmp_failure_pack
failure-doctor diagnose .\tmp_failure_pack --out .\tmp_collected_report
failure-doctor pack-logs .\examples\mock_raw_logs --out .\tmp_log_pack
failure-doctor diagnose .\tmp_log_pack --out .\tmp_log_report
```

See docs/INTEGRATIONS.md and docs/GITHUB_ACTION_USAGE.md.

## Validation Hardening Pack

Agent Failure Doctor v1.3 adds a multi-track validation gate:

```powershell
python -m tools.validation.run_validation_hardening
```

It writes `validation/v1_3_validation_hardening.json`.

The gate keeps template fixtures, public-inspired records, native Playwright traces, resolution validation, applied scenarios, external references, and integration smoke tests as separate evidence tiers. There is no single averaged accuracy score.

## Auto Capture Pack

Agent Failure Doctor v2.0 adds command auto capture:

```powershell
failure-doctor run -- python crawler.py
failure-doctor run -- pytest tests/test_listing.py
failure-doctor run -- playwright test
```

It writes `.failure-doctor/runs/<run_id>/` with command.txt, exit_code.txt, stdout.log, stderr.log, environment.json, detected_artifacts.json, input_summary.json, diagnosis/, fix_plan/, verification_hint.md, and shareable_failure_pack.zip.

`safe_to_share.json` defaults to `safe_to_share=false`; review and sanitize before sharing.

## Sanitize & Share Pack

Agent Failure Doctor v2.1 adds a conservative sharing step:

```powershell
failure-doctor sanitize .\.failure-doctor\runs\<run_id> --out .\shareable_failure_pack
```

It writes `sanitized_error.log`, `sanitized_network.json`, `sanitized_trace_metadata.json`, `redaction_report.json`, `safe_to_share.json`, `README_FOR_REVIEWER.md`, and `shareable_failure_pack.zip`.

Raw `trace.zip` is not copied into the sanitized pack. `safe_to_share.json` still defaults to `safe_to_share=false`; review the pack before sending it to a public issue or another developer.


