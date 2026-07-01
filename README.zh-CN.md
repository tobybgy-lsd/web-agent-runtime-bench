# Agent Failure Doctor 中文文档`r`n`r`n[English documentation](README.md)`r`n`r`n本地优先的自动化失败诊断、修复交接与安全合规评估工具。`r`n`r`n[English documentation](README.md)

![CI](https://github.com/tobybgy-lsd/web-agent-runtime-bench/actions/workflows/benchmark.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)

Agent Failure Doctor 閺勵垯绔存稉?*閺堫剙婀存导妯哄帥**閻ㄥ嫯鍤滈崝銊ュ婢惰精瑙︾拠濠冩焽瀹搞儱鍙块敍宀勬桨閸?AI Browser Agent閵嗕赋laywright閵嗕阜PA閵嗕胶鍩囬搹顐ュ殰閸斻劌瀵查崪灞炬殶閹诡噣鍣伴梿鍡氬壖閺堫剝鐨熺拠鏇樷偓?
- 瑜版挸澧犻柌宀€鈻肩喊鎴窗Agent Failure Doctor v3.3 Safety & Compliance Evaluation Pack
- 娑撳﹣绔存稉?P98 缁嬪啿鐣剧痪鍖＄窗Agent Failure Doctor v3.1.0 P98 Master Gate
- 娑撳﹣绔存稉?P95 缁嬪啿鐣剧痪鍖＄窗Agent Failure Doctor v2.4.1 P95 Alignment & Missing Tracks Pack

**鏉堟挸鍙嗛敍?* `trace.zip` / `error.log` / `console.txt` / `network.json` /
`probe_report.json` / `browser_runtime_report.json` / `input_timing_summary.json` / 閹搭亜娴?metadata / `user_description.txt`

**鏉堟挸鍤敍?* 鐠囧﹥鏌囩紒鎾诡啈閵嗕浇鐦夐幑顔衡偓浣风瑓娑撯偓濮濄儯鈧椒鎱ㄦ径宥呯紦鐠侇喓鈧笩itHub issue 閼藉顭堥妴?Codex 娣囶喖顦?Prompt閵嗕浇鍔氶弫蹇斿Г閸涘﹤瀵橀妴?
## 韫囶偊鈧喎绱戞慨?
```powershell
python -m pip install agent-failure-doctor
git clone https://github.com/tobybgy-lsd/web-agent-runtime-bench.git
cd web-agent-runtime-bench

failure-doctor diagnose .\examples\failed_runs\proxy_network_error --out .\report
failure-doctor plan .\report --out .\fix_plan
failure-doctor collect --project . --preset auto --out .\failure_doctor_auto_report `
  --auto-diagnose --auto-handoff --auto-sanitize
failure-doctor agent-bootstrap --target all --project .
```

## 閸掑棗褰傛稉搴ｆ埂鐎圭偛寮芥＃?
v3.3.0 閺勵垰缍嬮崜宥嚽旂€规碍濡ч張顖氱唨缁捐￥鈧倸鐣犻崷銊︽拱閸﹂绱崗鍫ｇ槚閺傤叀鍏橀崝娑楃婢舵牭绱濋弬鏉款杻
Safety & Compliance Evaluation閿涙碍顥呴弻?collector scope閵嗕够ecret 濞夊嫭绱￠妴?shareability閵嗕竸I handoff閵嗕垢atch proposal閵嗕笍OM 妞嬪酣娅撻妴浣规綀闂勬劘绔熼悾灞烩偓?閺佺増宓佹径鏍ㄧ閵嗕胶顬囩痪?cloud-browser artifact 閸?regulated workflow mock閵?
```powershell
failure-doctor safety-evaluate --project . --out .\safety_report
failure-doctor collect --project . --preset auto --out .\failure_doctor_auto_report --auto-diagnose --auto-handoff --auto-sanitize --safety-evaluate
```

鐠囥儴鐦庢导鏉跨湴娣囨繃瀵?local-only閵嗕躬vidence-only閵嗕苟o upload閵嗕苟o active probe閿?娑撳秵褰佹笟娑氱搏鏉╁洢鈧浇顫夐柆瑁も偓浣峰悏闁姰鈧胶鐗憴锝冣偓涔籵lver閵嗕線鈧艾鍙ч崳銊﹀灗缁変焦婀侀弬瑙勵攳閵?
- PyPI 閸欐垵绔烽幍瀣斀閿涙瓟docs/PYPI_RELEASE.md](docs/PYPI_RELEASE.md)
- 娑撹濮╅幒銏ゆ嫛鏉堝湱鏅敍姝攄ocs/ACTIVE_PROBE_BOUNDARY.md](docs/ACTIVE_PROBE_BOUNDARY.md)
- 鐞涘奔璐熸稉?Client Hints 鏉堝湱鏅敍姝攄ocs/BEHAVIORAL_CLIENT_HINTS_BOUNDARY.md](docs/BEHAVIORAL_CLIENT_HINTS_BOUNDARY.md)
- JavaScript 鐎瑰本鏆ｉ幀褑绔熼悾宀嬬窗[docs/JS_INTEGRITY_BOUNDARY.md](docs/JS_INTEGRITY_BOUNDARY.md)
- Canvas 閹稿洨姹楁潏鍦櫕閿涙瓟docs/CANVAS_FINGERPRINT_BOUNDARY.md](docs/CANVAS_FINGERPRINT_BOUNDARY.md)
- 2 閸掑棝鎸撳鏃傘仛閼存碍婀伴敍姝攄ocs/DEMO_VIDEO_SCRIPT.md](docs/DEMO_VIDEO_SCRIPT.md)
- 閹垛偓閺堫垱鏋冪粩鐘哄磸缁嬪尅绱癧docs/TECH_ARTICLE_DRAFT.md](docs/TECH_ARTICLE_DRAFT.md)
- 閻喎鐤勯悽銊﹀煕閸欏秹顩梻顓犲箚閿涙瓟docs/REAL_USER_FEEDBACK_LOOP.md](docs/REAL_USER_FEEDBACK_LOOP.md)

PyPI 閸欐垵绔烽崥搴ｆ畱閻╊喗鐖ｇ€瑰顥婇崨鎴掓姢閿?
```powershell
pip install agent-failure-doctor
```

## 娑撯偓闁款喗婀伴崷浼村櫚闂嗗棔绗岀拠濠冩焽

```powershell
failure-doctor collect --project . --preset auto --out .\failure_doctor_auto_report `
  --auto-diagnose --auto-handoff --auto-sanitize

failure-doctor watch --project . --out .\failure_reports --once --auto-diagnose
failure-doctor run --capture -- python .\examples\mock_script_fails.py
```

闂堢偞濡ч張?Windows 閻劍鍩涢崣顖欎簰閸欏苯鍤?`scripts/windows/Start-FailureDoctor-Diagnosis.bat`閿涘奔绡冮崣顖欎簰閹跺﹤銇戠拹銉┿€嶉惄顔芥瀮娴犺泛銇?閹锋牕鍩屾潻娆庨嚋 BAT 娑撳鈧?
`collect` 閸欘亝澹傞幓蹇庣稑閹哄牊娼堥惃鍕€嶉惄顔芥瀮娴犺泛銇欓敍灞肩瑝閹殿偅寮块弫鏉戝酱閻絻鍓抽敍灞肩瑝鐠囪褰囧ù蹇氼潔閸ｃ劎鏁ら幋鐤カ閺傛瑣鈧?閸戭厽宓佹惔鎾扁偓涓糞H key閵嗕梗.git`閵嗕梗node_modules` 閹存牞娅勯幏鐔哄箚婢у啰娲拌ぐ鏇礉娑旂喍绗夋导姘瑐娴肩姳鎹㈡担鏇熸瀮娴犺翰鈧?鐎电懓顦婚崚鍡曢煩閸撳秴褰ф惔鏃€鐓￠惇瀣嫙閸掑棔闊?`sanitized_failure_pack/`閵?
## AI 閸撳秶顏拫鍐暏

Agent Failure Doctor 閸欘垯浜掓担婊€璐熸稉宥呮倱 AI coding agent 閻ㄥ嫭婀伴崷鎷岀槚閺傤厼鎮楃粩顖ょ窗

```powershell
failure-doctor agent-bootstrap --target all --project .
```

鐎瑰啩绱伴悽鐔稿灇閿?
```text
.failure-doctor/
閳规壕鏀㈤埞鈧?AGENT_ENTRYPOINT.md
閳规柡鏀㈤埞鈧?agents/<target>/
    閳规壕鏀㈤埞鈧?instructions.md
    閳规壕鏀㈤埞鈧?diagnose_project.md
    閳规壕鏀㈤埞鈧?repair_workflow.md
    閳规壕鏀㈤埞鈧?allowed_commands.md
    閳规柡鏀㈤埞鈧?forbidden_actions.md
```

閺€顖涘瘮閻ㄥ嫬澧犵粩顖氬瘶閹奉剨绱?
`codex` / `cursor` / `claude_code` / `vscode_copilot` / `antigravity` /
`opencode` / `qoder` / `trae` / `workbuddy` / `openclaw` / `hermes` /
`generic_agent`

## 閻㈢喎鎳￠崨銊︽埂

```text
collect / run / adapt
  -> diagnose
  -> plan
  -> handoff / propose-patch
  -> verify
  -> sanitize / share
```

鐢摜鏁ら崨鎴掓姢閿?
```powershell
failure-doctor diagnose .\failed_run --out .\report
failure-doctor plan .\report --out .\fix_plan
failure-doctor handoff .\report --target codex --out .\ai_handoff
failure-doctor propose-patch --repo . --report .\report --out .\patch_plan
failure-doctor verify --before .\failed_run --after .\rerun_after_fix --out .\verification
failure-doctor sanitize .\failure_doctor_auto_report --out .\shareable_failure_pack
failure-doctor batch .\runs --out .\batch_report
```

## 閹躲儱鎲￠崘鍛啇

```text
report/
閳规壕鏀㈤埞鈧?diagnosis.json
閳规壕鏀㈤埞鈧?diagnosis.md
閳规壕鏀㈤埞鈧?evidence.json
閳规壕鏀㈤埞鈧?input_summary.json
閳规壕鏀㈤埞鈧?issue_draft.md
閳规壕鏀㈤埞鈧?repair_suggestions.md
閳规壕鏀㈤埞鈧?codex_fix_prompt.md
閳规柡鏀㈤埞鈧?failure_doctor_report.zip
```

閹躲儱鎲℃导姘愁嚛閺勫函绱?
- 閺堚偓閸欘垵鍏橀惃鍕亼鐠愩儳琚崚顐㈡嫲閹垛偓閺堫垰鐡欑猾?- 閺€顖涙嫼閸掋倖鏌囬惃鍕槈閹?- 缂傚搫鐨崫顏冪昂閺夋劖鏋?- 娣囶喖顦插楦款唴閸滃矂鐛欑拠浣告嚒娴?- 閸欘垯浜掓禍銈囩舶 Codex / Claude Code / Cursor 閻ㄥ嫪鎱ㄦ径?Prompt

## 瑜版挸澧犳宀冪槈

- P98 master gate閿涙岸鈧俺绻?- Auto Collector validation閿?5 娑擃亝婀伴崷?fixture case閿涘矂鈧俺绻?- 鐎瑰鍙忛幍顐ｅ伎閿? forbidden output
- GitHub Actions閿涙瓙indows / Ubuntu / macOS 閸у洩绻嶇悰灞藉礋濞村鎷版宀冪槈

閺屻儳婀呴敍?
- [Validation Dashboard](validation/dashboard.md)
- [P98 Limits](docs/P98_LIMITS.md)
- [Agent Frontend Invocation](docs/AGENT_FRONTEND_INVOCATION.md)
- [Safety Boundary](docs/safety_boundary.md)

## 鐎瑰鍙忔潏鍦櫕

閺堫剟銆嶉惄顔煎涧閸嬫碍婀伴崷鑸偓浣瑰房閺夊啨鈧浇鍔氶弫蹇旀綏閺傛瑧娈戞径杈Е鐠囧﹥鏌囬妴?
鐎瑰啩绗夐弰顖ょ窗

- CAPTCHA 婢跺嫮鎮婂銉ュ徔
- 妞嬪孩甯剁憴鍕缉瀹搞儱鍙?- 閹稿洨姹楁导顏堚偓鐘蹭紣閸?- 閸戭厽宓侀幓鎰絿瀹搞儱鍙?- 閺堫亝宸块弶鍐櫚闂嗗棗浼愰崗?- 閻喎鐤勯獮鍐插酱闁插洭娉﹀鍡樼仸

婵″倹鐏夌拠濠冩焽缂佹挻鐏夐弰鍓с仛閻ゆ垳鎶€鐠佸潡妫堕梽鎰煑閹存牕鎮庣憴鍕棑闂勨晪绱濆銉ュ徔閸欘亙绱扮紒娆忓毉鐎瑰鍙忛崚鍡樼ウ瀵ら缚顔呴敍?绾喛顓婚幒鍫熸綀閵嗕線妾锋担搴ゎ嚞濮瑰倿鍣洪妴浣峰▏閻劌鐣奸弬?API閵嗕浇浠堢化璇查挬閸欒埇鈧焦鏁奸幋鎰眽瀹搞儱顓搁弽鍛婄ウ缁嬪鍨ㄩ崑婊勵剾閼奉亜濮╅崠鏍モ偓?
## 鐠愶紕灏炴径杈Е濡楀牅绶?
娴ｇ姳绗夐棁鈧憰浣稿晸娴狅絿鐖滈妴鍌涙付閺堝鐜崐鑲╂畱鐠愶紕灏為弰顖涘絹娴溿倓绔存稉顏囧姎閺佸繐銇戠拹銉︻攳娓氬鈧?
濞嗐垼绻嬮幓鎰唉閼磋鲸鏅遍崥搴ｆ畱閿?
- `error.log`
- `trace.zip`
- `console.txt`
- `network.json`
- screenshot metadata
- `user_description.txt`

娑撳秷顩﹂幓鎰唉鐎靛棛鐖滈妴涔okie閵嗕辜oken閵嗕工uthorization header閵嗕竸PI key閵嗕胶顫嗛張?URL閵?娑擃亙姹夐弫鐗堝祦閵嗕礁顓归幋閿嬫殶閹诡喗鍨ㄦ禒璁崇秿閺佸繑鍔呮穱鈩冧紖閵?
婵″倹鐏夋担鐘插帒鐠侀潻绱濋柅鍌氭値閸忣剙绱戦惃鍕攳娓氬绱版潻娑樺弳 validation corpus閵嗗倹膩閺夊灝鎷版担婊嗏偓鍛板殰瀹歌京鏁撻幋鎰畱
缁€杞扮伐娑撳秷顓搁崗銉ヮ樆闁劑鐛欑拠浣瑰瘹閺嶅洢鈧?