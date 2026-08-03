# GROK COMPLETION 7 REWORK 5 TRIAGE — r6 baseline 失败证据分类
**执行者：** Grok（r6 证据分类；非 Gate 独立审查者）  
**日期：** 2026-07-29  
**任务卡：** `docs/fixes/handoffs/CODEX_TASK_7_REWORK_5_TRIAGE.md`  
**证据根（只读）：** `C:\Users\Administrator\gate1-evidence\20260729-1715-dc83140-grok-r6\`  
**本轮：未重跑任何 pytest/Ruff/Gate/smoke。**

---

## 5.1 r6 不变事实

| 项 | baseline | candidate |
|----|----------|----------|
| COMMAND_EXIT | 1 | 1 |
| TEE_EXIT | 0 | 0 |
| summary | 123 failed, 14926 passed, 103 skipped, 7 xfailed, 3 errors, … 4391.56s | 123 failed, 15006 passed, … 4559.10s |
| JUnit | 可解析 junit-ok | 可解析 junit-ok |
| fail-ids (dotted) | **126** | **126** |
| 集合关系 | 两侧 **完全相等**；`new-failures.txt` **空** |

说明：失败集相等只证明 candidate **无新增**；相对 PASS 仍需每项 known 依据（本文件）。

---

## 5.2 根因组

SECTION/GROUP 数量（有映射的组）：**30**

### GROUP `ENV_MISSING_PSYCOPG`
- category: `known_environment`
- relative_gate_eligible: `yes`
- node_count: `3`
- root_cause: Gate 环境 `uv sync --locked --extra dev --extra all` 未提供可导入的 `psycopg` 包；`tests.db.test_utils` 在 import/连接层直接 ModuleNotFoundError。
- evidence: r6 baseline-junit: ModuleNotFoundError: No module named 'psycopg'；baseline-packages.txt 无 psycopg；与 candidate 包列表 cmp 一致。
- limitation: 未验证安装 psycopg 后是否全绿；仅证明当前 Gate 依赖矩阵缺该模块。

### GROUP `ENV_MISSING_DEPLOY_DOCKER`
- category: `known_environment`
- relative_gate_eligible: `yes`
- node_count: `6`
- root_cause: 测试导入 `deploy.docker` 失败：该模块不在当前工作树可导入路径/未作为已安装发行件暴露，属 Gate 树/打包布局环境限制，非 candidate 独有 diff。
- evidence: r6 baseline-junit: ModuleNotFoundError: No module named 'deploy.docker'；nodeid 前缀 tests.deploy.test_docker_entrypoint_import。
- limitation: 未区分是缺包还是 PYTHONPATH/包名布局问题。

### GROUP `ENV_POLLY_RESOURCE_NOT_DIRECTORY`
- category: `known_environment`
- relative_gate_eligible: `yes`
- node_count: `3`
- root_cause: `omnigent/resources/examples/polly` 在 baseline 树中不是目录（Errno 20 Not a directory），导致 ensure_default_polly setup 失败。常见于资源被检成单文件/损坏布局，属工作树资源形态环境问题。
- evidence: r6 baseline-junit error: NotADirectoryError: .../omnigent/resources/examples/polly；3 个 test_ensure_default_polly_agent_* setup error。
- limitation: 未在本机 ls -la 该路径（只读 JUnit）；根因归类依赖错误消息路径。

### GROUP `ENV_BUNDLED_EXAMPLE_NOT_DIRECTORY`
- category: `known_environment`
- relative_gate_eligible: `yes`
- node_count: `9`
- root_cause: 打包示例 polly/debby 资源无法作为目录/YAML mapping 解析（ClickException expected YAML mapping got str；或 agent 未注册/路径不一致）。与 examples 资源布局/安装形态相关，main baseline 与 candidate 同失败。
- evidence: r6 JUnit: examples/polly|debby expected YAML mapping got str；polly/debby was not registered；Debby packaged path assertion。
- limitation: 与 ENV_POLLY_RESOURCE_NOT_DIRECTORY 可能同源；未单独拆分 LFS/文件类型。

### GROUP `ENV_NO_RUNNER_BOUND`
- category: `known_environment`
- relative_gate_eligible: `yes`
- node_count: `16`
- root_cause: 集成测试调用需要已绑定 runner 的 session API，但 Gate 隔离环境未提供绑定 runner；服务返回 503 runner_unavailable / No runner bound for session。
- evidence: r6 baseline-junit 重复消息 runner_unavailable: No runner bound for session；HTTP 503；nodeid 多为 tests.server.integration.* 与部分 routes。
- limitation: 未证明生产 AgentCenter 配置下会通过；仅证明当前 Gate 无 runner 绑定。

### GROUP `ENV_ISOLATED_HOME_NO_DEFAULT_CREDENTIAL`
- category: `known_environment`
- relative_gate_eligible: `yes`
- node_count: `3`
- root_cause: r6 使用空隔离 HOME seed，无用户 credentials；bundled agent 启动期望 credential map 含 'default' 键，得到 None。
- evidence: r6 JUnit: assert None is True ... dict.get('default') 于 anthropic credential 映射；baseline-home-before 与 seed cmp 为空目录形态。
- limitation: 未注入假 credential 复测。

### GROUP `ENV_BWRAP_EGRESS_NETWORK`
- category: `known_environment`
- relative_gate_eligible: `yes`
- node_count: `1`
- root_cause: linux_bwrap egress e2e 出站 HTTPS 被拒：Tunnel connection failed: 403；属沙箱/出口网络或代理环境限制。
- evidence: r6 JUnit AssertionError 含 Tunnel connection failed: 403 Forbidden。
- limitation: 未区分公司代理/CI 出口策略细节。

### GROUP `MAIN_INTEGRATION_HANG_TIMEOUT`
- category: `known_main_code_failure`
- relative_gate_eligible: `no`
- node_count: `11`
- root_cause: 集成测试在 300s 内未完成（pytest-timeout）或 asyncio TimeoutError；单次 run 的超时不能自动标 flaky，表现为 main 集成路径挂起/未收敛。
- evidence: r6 JUnit: Failed: Timeout (>300.0s) from pytest-timeout 或 TimeoutError；nodeid 含 runner_ownership / session_host_launch / elicitation / policy ask。
- limitation: 无第二次独立 run 证明 flaky 交替 pass/fail；故不可 relative eligible。

### GROUP `MAIN_POLICY_FIXTURE_KEYERROR_AG_TEST`
- category: `known_main_code_failure`
- relative_gate_eligible: `no`
- node_count: `10`
- root_cause: policy 路由测试期望 agent 键 'ag_test/abc123' 存在，运行时 KeyError；main 代码/测试夹具契约不一致。
- evidence: r6 JUnit KeyError: 'ag_test/abc123' 于 tests.server.routes.test_sessions_policy。
- limitation: none

### GROUP `MAIN_POLICY_ENGINE_ALLOWS_UNEXPECTED`
- category: `known_main_code_failure`
- relative_gate_eligible: `no`
- node_count: `10`
- root_cause: 策略引擎返回 POLICY_ACTION_ALLOW，断言期望 DENY/ASK；main 上 policy 组合/函数策略/默认策略行为与测试契约不符。
- evidence: r6 JUnit assert 'POLICY_ACTION_ALLOW' == 'POLICY_ACTION_DENY'|ASK；policy_composition_e2e / policy_evaluate / input deny。
- limitation: none

### GROUP `MAIN_POLICY_READ_ONLY_PHASE`
- category: `known_main_code_failure`
- relative_gate_eligible: `no`
- node_count: `2`
- root_cause: read-only policy evaluate 未写入 expected labels/phase（None）。
- evidence: r6 JUnit LEVEL_EDIT labels / Phase.REQUEST is None。
- limitation: none

### GROUP `MAIN_FORK_NATIVE_CARRY_FLAGS`
- category: `known_main_code_failure`
- relative_gate_eligible: `no`
- node_count: `14`
- root_cause: fork 路由未设置 carry_history_into_native / copy_model_settings 等期望标志（assert False is True）。
- evidence: r6 JUnit tests.server.routes.test_sessions_fork::* carry/copy flags。
- limitation: none

### GROUP `MAIN_CURSOR_FORWARDER_STATE`
- category: `known_main_code_failure`
- relative_gate_eligible: `no`
- node_count: `5`
- root_cause: cursor native forwarder 测试未到达期望状态（wedged?）。
- evidence: r6 JUnit: forwarder never reached the expected state (wedged?)。
- limitation: 可能含时序因素，但单次 run 不足标 flaky。

### GROUP `MAIN_RELAY_STATUS_STAYS_IDLE`
- category: `known_main_code_failure`
- relative_gate_eligible: `no`
- node_count: `8`
- root_cause: relay/list sessions 状态仍为 idle，断言期望 running/failed/busy。
- evidence: r6 JUnit assert 'idle' == 'running'|'failed'；child_sessions busy False。
- limitation: none

### GROUP `MAIN_TEST_DB_GUARDRAIL_HEURISTIC`
- category: `known_main_code_failure`
- relative_gate_eligible: `no`
- node_count: `6`
- root_cause: looks_like_test_db 启发式与测试期望相反（把 testing.db 等判为测试库）。
- evidence: r6 JUnit looks_like_test_db('sqlite:///testing.db') is True 期望 False。
- limitation: none

### GROUP `MAIN_RESPONSE_ID_HEX_SUFFIX`
- category: `known_main_code_failure`
- relative_gate_eligible: `no`
- node_count: `2`
- root_cause: executor adapter 解析 response id 时 Invalid hex suffix（resp_reason/resp_model）。
- evidence: r6 JUnit ValueError Invalid hex suffix in 'resp_reason'|'resp_model'。
- limitation: none

### GROUP `MAIN_CLI_ALLOWLIST_PLATFORM_INFO`
- category: `known_main_code_failure`
- relative_gate_eligible: `no`
- node_count: `1`
- root_cause: CLI 注册了 platform-info 但未列入 _CLICK_SUBCOMMANDS allowlist。
- evidence: r6 JUnit missing from _CLICK_SUBCOMMANDS: ['platform-info']。
- limitation: none

### GROUP `MAIN_MANAGED_LAUNCH_NOT_SETTLED`
- category: `known_main_code_failure`
- relative_gate_eligible: `no`
- node_count: `1`
- root_cause: managed launch 事件未 settled。
- evidence: r6 JUnit create launch never settled ManagedLaunch settled unset。
- limitation: none

### GROUP `MAIN_RUNNER_PARENT_EXIT_PID`
- category: `known_main_code_failure`
- relative_gate_eligible: `no`
- node_count: `1`
- root_cause: 父进程退出后子 runner PID 仍存活（_pid_alive True）。
- evidence: r6 JUnit assert not True = _pid_alive(...)。
- limitation: none

### GROUP `MAIN_UPDATE_VERSIONS_CHECK`
- category: `known_main_code_failure`
- relative_gate_eligible: `no`
- node_count: `1`
- root_cause: update_versions check 期望抛 ValueError 但未抛出。
- evidence: r6 JUnit Failed: DID NOT RAISE ValueError。
- limitation: none

### GROUP `MAIN_USAGE_OBSERVER_KEYERROR`
- category: `known_main_code_failure`
- relative_gate_eligible: `no`
- node_count: `1`
- root_cause: usage observer 缺少 key test_nonstream。
- evidence: r6 JUnit KeyError: 'test_nonstream'。
- limitation: none

### GROUP `MAIN_RUNNER_REBIND_NOT_REGISTERED`
- category: `known_main_code_failure`
- relative_gate_eligible: `no`
- node_count: `1`
- root_cause: PATCH runner 重绑时 runner_recovered 未注册 → 400。
- evidence: r6 JUnit invalid_input runner 'runner_recovered' is not registered。
- limitation: none

### GROUP `MAIN_MCP_CACHE_EVICT`
- category: `known_main_code_failure`
- relative_gate_eligible: `no`
- node_count: `1`
- root_cause: delete session 后 MCP startup cache 未按预期驱逐。
- evidence: r6 JUnit session id not in cache dict {}。
- limitation: none

### GROUP `MAIN_INTERRUPT_FENCE`
- category: `known_main_code_failure`
- relative_gate_eligible: `no`
- node_count: `1`
- root_cause: interrupt 成功后 stop fence 未保留。
- evidence: r6 JUnit fence installed assert session id in set()。
- limitation: none

### GROUP `MAIN_TUNNEL_RELAY_SPAWN`
- category: `known_main_code_failure`
- relative_gate_eligible: `no`
- node_count: `1`
- root_cause: PATCH-bind 未 spawn relay。
- evidence: r6 JUnit PATCH-bind did not spawn a relay assert None is not None。
- limitation: none

### GROUP `MAIN_TERMINAL_CREATE_HTTP`
- category: `known_main_code_failure`
- relative_gate_eligible: `no`
- node_count: `3`
- root_cause: create terminal 代理返回 400 或错误消息形状与断言不符。
- evidence: r6 JUnit assert 400==200|500；undeclared terminal message 不含 bash。
- limitation: none

### GROUP `MAIN_INPUT_POLICY_DENY_PAYLOAD`
- category: `known_main_code_failure`
- relative_gate_eligible: `no`
- node_count: `1`
- root_cause: input policy deny 持久化 payload/reason 与期望不符。
- evidence: r6 JUnit denied payload reason 差异 ASK_THIS_TOKEN vs policy evaluation error。
- limitation: none

### GROUP `MAIN_MCP_PROXY_ELICIT_POP`
- category: `known_main_code_failure`
- relative_gate_eligible: `no`
- node_count: `1`
- root_cause: events handler 未 pop from_mcp=False elicitation 条目。
- evidence: r6 JUnit from_mcp=False entry was NOT popped。
- limitation: none

### GROUP `MAIN_SNAPSHOT_MODEL_OPTIONS_RETRY`
- category: `known_main_code_failure`
- relative_gate_eligible: `no`
- node_count: `2`
- root_cause: session snapshot 对 codex-model-options 重试次数为 1 期望 2。
- evidence: r6 JUnit assert 1 == 2 count(.../codex-model-options)。
- limitation: none

### GROUP `MAIN_SNAPSHOT_SKILLS_PUBLISH`
- category: `known_main_code_failure`
- relative_gate_eligible: `no`
- node_count: `1`
- root_cause: fetch resolve 后未发布 session.skills 事件。
- evidence: r6 JUnit Expected exactly 1 session.skills publish, got 0。
- limitation: none

---

## 5.3 可机器核对的 126 项映射

```text
BEGIN_NODE_MAP
tests.cli.test_chat::test_materialize_bundle_overrides_brain_harness[debby-expected_workers1-openai-agents]	failure	ENV_BUNDLED_EXAMPLE_NOT_DIRECTORY	yes
tests.cli.test_chat::test_materialize_bundle_overrides_brain_harness[debby-expected_workers1-pi]	failure	ENV_BUNDLED_EXAMPLE_NOT_DIRECTORY	yes
tests.cli.test_chat::test_materialize_bundle_overrides_brain_harness[polly-expected_workers0-openai-agents]	failure	ENV_BUNDLED_EXAMPLE_NOT_DIRECTORY	yes
tests.cli.test_chat::test_materialize_bundle_overrides_brain_harness[polly-expected_workers0-pi]	failure	ENV_BUNDLED_EXAMPLE_NOT_DIRECTORY	yes
tests.cli.test_cli::test_bundled_agent_launches_with_first_available_credential[debby]	failure	ENV_ISOLATED_HOME_NO_DEFAULT_CREDENTIAL	yes
tests.cli.test_cli::test_bundled_agent_launches_with_first_available_credential[polly]	failure	ENV_ISOLATED_HOME_NO_DEFAULT_CREDENTIAL	yes
tests.cli.test_cli::test_bundled_agent_multiple_credentials_notice_preserves_first_pick	failure	ENV_ISOLATED_HOME_NO_DEFAULT_CREDENTIAL	yes
tests.cli.test_cli::test_click_subcommands_allowlist_covers_registered_commands	failure	MAIN_CLI_ALLOWLIST_PLATFORM_INFO	no
tests.db.test_utils::test_create_engine_wires_token_refresh_and_short_recycle	failure	ENV_MISSING_PSYCOPG	yes
tests.db.test_utils::test_static_postgres_uri_path_unchanged	failure	ENV_MISSING_PSYCOPG	yes
tests.db.test_utils::test_token_callback_invoked_per_connection	failure	ENV_MISSING_PSYCOPG	yes
tests.deploy.test_docker_entrypoint_import::test_entrypoint_imports_without_side_effects	failure	ENV_MISSING_DEPLOY_DOCKER	yes
tests.deploy.test_docker_entrypoint_import::test_resolve_config_captures_s3_artifact_uri	failure	ENV_MISSING_DEPLOY_DOCKER	yes
tests.deploy.test_docker_entrypoint_import::test_resolve_config_defaults_to_no_remote_store	failure	ENV_MISSING_DEPLOY_DOCKER	yes
tests.deploy.test_docker_entrypoint_import::test_resolve_config_rejects_non_s3_artifact_uri	failure	ENV_MISSING_DEPLOY_DOCKER	yes
tests.deploy.test_docker_entrypoint_import::test_select_artifact_store[None-LocalArtifactStore]	failure	ENV_MISSING_DEPLOY_DOCKER	yes
tests.deploy.test_docker_entrypoint_import::test_select_artifact_store[s3://my-bucket/artifacts-S3ArtifactStore]	failure	ENV_MISSING_DEPLOY_DOCKER	yes
tests.inner.sandbox.test_egress_e2e::test_egress_allows_matching_https_get[linux_bwrap]	failure	ENV_BWRAP_EGRESS_NETWORK	yes
tests.llms.test_usage_observer::test_client_notify_records_with_active_test	failure	MAIN_USAGE_OBSERVER_KEYERROR	no
tests.runtime.harnesses.test_executor_adapter::test_executor_adapter_builds_config_from_request	failure	MAIN_RESPONSE_ID_HEX_SUFFIX	no
tests.runtime.harnesses.test_executor_adapter::test_executor_adapter_forwards_model_override_to_config	failure	MAIN_RESPONSE_ID_HEX_SUFFIX	no
tests.runtime.harnesses.test_process_manager::test_runner_subprocess_exits_when_spawning_parent_exits	failure	MAIN_RUNNER_PARENT_EXIT_PID	no
tests.scripts.test_update_versions::test_check_detects_missing_pin	failure	MAIN_UPDATE_VERSIONS_CHECK	no
tests.server.integration.test_host_session_binding::test_managed_launch_progress_surfaces_on_snapshot_and_stream	failure	MAIN_INTEGRATION_HANG_TIMEOUT	no
tests.server.integration.test_host_session_binding::test_message_relaunches_dead_managed_sandbox	failure	MAIN_MANAGED_LAUNCH_NOT_SETTLED	no
tests.server.integration.test_policy_composition_e2e::test_ask_fires_when_deny_removed	failure	MAIN_POLICY_ENGINE_ALLOWS_UNEXPECTED	no
tests.server.integration.test_policy_composition_e2e::test_deny_overrides_allow	failure	MAIN_POLICY_ENGINE_ALLOWS_UNEXPECTED	no
tests.server.integration.test_policy_composition_e2e::test_deny_takes_precedence_over_ask	failure	MAIN_POLICY_ENGINE_ALLOWS_UNEXPECTED	no
tests.server.integration.test_policy_composition_e2e::test_two_deny_policies_first_reason_visible	failure	MAIN_POLICY_ENGINE_ALLOWS_UNEXPECTED	no
tests.server.integration.test_runner_ownership::test_bind_own_runner_succeeds	timeout	MAIN_INTEGRATION_HANG_TIMEOUT	no
tests.server.integration.test_runner_ownership::test_fork_is_unbound_and_only_forker_can_bind_runner	timeout	MAIN_INTEGRATION_HANG_TIMEOUT	no
tests.server.integration.test_runner_ownership::test_parent_session_runner_inheritance_blocked_cross_user	timeout	MAIN_INTEGRATION_HANG_TIMEOUT	no
tests.server.integration.test_session_host_launch::test_host_session_message_waits_for_bound_runner_before_relaunch	timeout	MAIN_INTEGRATION_HANG_TIMEOUT	no
tests.server.integration.test_session_host_launch::test_message_relaunch_harness_not_configured_persists_error_turn	failure	MAIN_INTEGRATION_HANG_TIMEOUT	no
tests.server.integration.test_session_host_launch::test_relaunch_posts_session_init_before_forwarding_message	failure	ENV_NO_RUNNER_BOUND	yes
tests.server.integration.test_sessions_attribution::test_input_consumed_event_carries_created_by	failure	ENV_NO_RUNNER_BOUND	yes
tests.server.integration.test_sessions_attribution::test_post_event_records_authenticated_poster	failure	ENV_NO_RUNNER_BOUND	yes
tests.server.integration.test_sessions_child_sessions::test_child_sessions_busy_reflects_relay_status_cache[running-True]	failure	MAIN_RELAY_STATUS_STAYS_IDLE	no
tests.server.integration.test_sessions_child_sessions::test_child_sessions_busy_reflects_relay_status_cache[waiting-True]	failure	MAIN_RELAY_STATUS_STAYS_IDLE	no
tests.server.integration.test_sessions_child_sessions::test_child_sessions_per_child_fields_isolated_across_fanout	failure	MAIN_RELAY_STATUS_STAYS_IDLE	no
tests.server.integration.test_sessions_elicitation_resolve_url::test_child_mcp_input_required_bubbles_to_parent_stream	failure	MAIN_INTEGRATION_HANG_TIMEOUT	no
tests.server.integration.test_sessions_elicitation_resolve_url::test_child_policy_elicitation_bubbles_to_parent_stream	failure	MAIN_INTEGRATION_HANG_TIMEOUT	no
tests.server.integration.test_sessions_endpoints::test_delete_session_evicts_mcp_startup_cache	failure	MAIN_MCP_CACHE_EVICT	no
tests.server.integration.test_sessions_endpoints::test_interrupt_forward_success_keeps_stop_fence	failure	MAIN_INTERRUPT_FENCE	no
tests.server.integration.test_sessions_endpoints::test_list_sessions_reflects_relay_status_cache[failed-failed]	failure	MAIN_RELAY_STATUS_STAYS_IDLE	no
tests.server.integration.test_sessions_endpoints::test_list_sessions_reflects_relay_status_cache[running-running]	failure	MAIN_RELAY_STATUS_STAYS_IDLE	no
tests.server.integration.test_sessions_endpoints::test_list_sessions_reflects_relay_status_cache[waiting-running]	failure	MAIN_RELAY_STATUS_STAYS_IDLE	no
tests.server.integration.test_sessions_endpoints::test_list_sessions_rolls_up_busy_child_status	failure	MAIN_RELAY_STATUS_STAYS_IDLE	no
tests.server.integration.test_sessions_endpoints::test_patch_runner_rebind_clears_stale_failed_status	failure	MAIN_RUNNER_REBIND_NOT_REGISTERED	no
tests.server.integration.test_sessions_endpoints::test_post_external_session_status_idle_forwards_persisted_assistant_output	failure	ENV_NO_RUNNER_BOUND	yes
tests.server.integration.test_sessions_endpoints::test_post_external_session_status_propagates_runner_delivery_failure	failure	ENV_NO_RUNNER_BOUND	yes
tests.server.integration.test_sessions_endpoints::test_session_snapshot_reflects_terminal_pending_cache	failure	MAIN_RELAY_STATUS_STAYS_IDLE	no
tests.server.integration.test_sessions_endpoints::test_skill_slash_command_keeps_existing_title	failure	ENV_NO_RUNNER_BOUND	yes
tests.server.integration.test_sessions_endpoints::test_skill_slash_command_non_json_resolve_surfaces_controlled_error	failure	ENV_NO_RUNNER_BOUND	yes
tests.server.integration.test_sessions_endpoints::test_skill_slash_command_persists_visible_item_and_hidden_meta_message	failure	ENV_NO_RUNNER_BOUND	yes
tests.server.integration.test_sessions_harness_override::test_runner_body_omits_harness_override_when_unset	failure	ENV_NO_RUNNER_BOUND	yes
tests.server.integration.test_sessions_harness_override::test_runner_first_event_forwards_harness_override	failure	ENV_NO_RUNNER_BOUND	yes
tests.server.integration.test_sessions_model_override::test_create_time_model_override_forwards_on_first_event	failure	ENV_NO_RUNNER_BOUND	yes
tests.server.integration.test_sessions_model_override::test_per_event_model_override_wins_over_persisted	failure	ENV_NO_RUNNER_BOUND	yes
tests.server.integration.test_sessions_model_override::test_runner_path_forwards_persisted_model_override	failure	ENV_NO_RUNNER_BOUND	yes
tests.server.integration.test_sessions_model_override::test_smart_routing_overrides_orchestrator_model_for_child_session	failure	ENV_NO_RUNNER_BOUND	yes
tests.server.integration.test_sessions_policy_evaluate::test_evaluate_endpoint_passes_actor_to_policy	failure	MAIN_POLICY_ENGINE_ALLOWS_UNEXPECTED	no
tests.server.integration.test_sessions_policy_evaluate::test_llm_request_deny_by_function_policy	failure	MAIN_POLICY_ENGINE_ALLOWS_UNEXPECTED	no
tests.server.integration.test_sessions_policy_evaluate::test_llm_response_deny_by_function_policy	failure	MAIN_POLICY_ENGINE_ALLOWS_UNEXPECTED	no
tests.server.integration.test_sessions_policy_evaluate::test_tool_call_ask_forwards_popup_event_to_runner	failure	MAIN_INTEGRATION_HANG_TIMEOUT	no
tests.server.integration.test_sessions_policy_evaluate::test_tool_call_ask_holds_gate_and_returns_allow_on_accept	failure	MAIN_INTEGRATION_HANG_TIMEOUT	no
tests.server.integration.test_sessions_policy_evaluate::test_tool_call_ask_returns_deny_on_decline	failure	MAIN_INTEGRATION_HANG_TIMEOUT	no
tests.server.integration.test_sessions_policy_evaluate::test_tool_call_deny_with_default_policy	failure	MAIN_POLICY_ENGINE_ALLOWS_UNEXPECTED	no
tests.server.integration.test_sessions_policy_evaluate::test_tool_result_deny_with_default_policy	failure	MAIN_POLICY_ENGINE_ALLOWS_UNEXPECTED	no
tests.server.integration.test_sessions_policy_evaluate_read_only::test_edit_caller_persists_labels_as_before	failure	MAIN_POLICY_READ_ONLY_PHASE	no
tests.server.integration.test_sessions_policy_evaluate_read_only::test_request_phase_ask_decline_collapses_to_deny	failure	MAIN_POLICY_ENGINE_ALLOWS_UNEXPECTED	no
tests.server.integration.test_sessions_policy_evaluate_read_only::test_request_phase_ask_parks_server_side_and_collapses_to_allow	failure	MAIN_POLICY_READ_ONLY_PHASE	no
tests.server.integration.test_sessions_tool_result_forward::test_function_call_output_forwarded_as_tool_result	failure	ENV_NO_RUNNER_BOUND	yes
tests.server.integration.test_sessions_tunnel_three_layer::test_on_runner_connect_restarts_relay_via_router	failure	MAIN_TUNNEL_RELAY_SPAWN	no
tests.server.routes.test_session_resources::test_create_terminal_proxies_to_runner	failure	MAIN_TERMINAL_CREATE_HTTP	no
tests.server.routes.test_session_resources::test_create_terminal_rejected_for_undeclared_name	failure	MAIN_TERMINAL_CREATE_HTTP	no
tests.server.routes.test_session_resources::test_create_terminal_surfaces_runner_error_without_crashing[500-runner_payload1-500-internal_error-Terminal launch failed (runner returned HTTP 500)]	failure	MAIN_TERMINAL_CREATE_HTTP	no
tests.server.routes.test_session_resources::test_create_terminal_surfaces_runner_error_without_crashing[503-runner_payload0-503-runner_unavailable-tunnel closed before request completed]	failure	ENV_NO_RUNNER_BOUND	yes
tests.server.routes.test_sessions_fork::test_fork_cursor_pi_native_carry_gating[cursor-native-True]	failure	MAIN_FORK_NATIVE_CARRY_FLAGS	no
tests.server.routes.test_sessions_fork::test_fork_cursor_pi_native_carry_gating[pi-native-True]	failure	MAIN_FORK_NATIVE_CARRY_FLAGS	no
tests.server.routes.test_sessions_fork::test_fork_no_switch_native_source_carries_history	failure	MAIN_FORK_NATIVE_CARRY_FLAGS	no
tests.server.routes.test_sessions_fork::test_fork_reversed_native_spelling_carry_gating[native-claude-True]	failure	MAIN_FORK_NATIVE_CARRY_FLAGS	no
tests.server.routes.test_sessions_fork::test_fork_reversed_native_spelling_carry_gating[native-codex-True]	failure	MAIN_FORK_NATIVE_CARRY_FLAGS	no
tests.server.routes.test_sessions_fork::test_fork_reversed_native_spelling_carry_gating[native-cursor-True]	failure	MAIN_FORK_NATIVE_CARRY_FLAGS	no
tests.server.routes.test_sessions_fork::test_fork_reversed_native_spelling_carry_gating[native-pi-True]	failure	MAIN_FORK_NATIVE_CARRY_FLAGS	no
tests.server.routes.test_sessions_fork::test_fork_switch_model_and_carry_gating[claude-native-claude_sdk-True-False-True-expect_presentation5]	failure	MAIN_FORK_NATIVE_CARRY_FLAGS	no
tests.server.routes.test_sessions_fork::test_fork_switch_model_and_carry_gating[claude_sdk-claude-native-True-True-True-expect_presentation0]	failure	MAIN_FORK_NATIVE_CARRY_FLAGS	no
tests.server.routes.test_sessions_fork::test_fork_switch_model_and_carry_gating[claude_sdk-codex-native-False-True-False-expect_presentation1]	failure	MAIN_FORK_NATIVE_CARRY_FLAGS	no
tests.server.routes.test_sessions_fork::test_fork_switch_model_and_carry_gating[claude_sdk-cursor-native-False-True-False-expect_presentation2]	failure	MAIN_FORK_NATIVE_CARRY_FLAGS	no
tests.server.routes.test_sessions_fork::test_fork_switch_model_and_carry_gating[claude_sdk-pi-native-False-True-False-expect_presentation3]	failure	MAIN_FORK_NATIVE_CARRY_FLAGS	no
tests.server.routes.test_sessions_fork::test_fork_switch_model_and_carry_gating[claude_sdk-qwen-native-False-True-False-expect_presentation4]	failure	MAIN_FORK_NATIVE_CARRY_FLAGS	no
tests.server.routes.test_sessions_fork::test_fork_switch_model_and_carry_gating[openai-agents-claude-native-False-True-False-expect_presentation6]	failure	MAIN_FORK_NATIVE_CARRY_FLAGS	no
tests.server.routes.test_sessions_input_policy_deny::test_input_policy_deny_persists_item_readable_from_items_api	failure	MAIN_INPUT_POLICY_DENY_PAYLOAD	no
tests.server.routes.test_sessions_mcp_proxy_policy_retry::test_non_mcp_entry_popped_by_events_handler_on_accept	failure	MAIN_MCP_PROXY_ELICIT_POP	no
tests.server.routes.test_sessions_policy::test_allow_verdict	failure	MAIN_POLICY_FIXTURE_KEYERROR_AG_TEST	no
tests.server.routes.test_sessions_policy::test_deny_verdict	failure	MAIN_POLICY_FIXTURE_KEYERROR_AG_TEST	no
tests.server.routes.test_sessions_policy::test_input_allow_verdict	failure	MAIN_POLICY_FIXTURE_KEYERROR_AG_TEST	no
tests.server.routes.test_sessions_policy::test_input_ask_approved_falls_through_to_allow	failure	MAIN_POLICY_FIXTURE_KEYERROR_AG_TEST	no
tests.server.routes.test_sessions_policy::test_input_ask_declined_denies	failure	MAIN_POLICY_FIXTURE_KEYERROR_AG_TEST	no
tests.server.routes.test_sessions_policy::test_input_deny_verdict	failure	MAIN_POLICY_FIXTURE_KEYERROR_AG_TEST	no
tests.server.routes.test_sessions_policy::test_input_no_guardrails_skips_policy	failure	MAIN_POLICY_FIXTURE_KEYERROR_AG_TEST	no
tests.server.routes.test_sessions_policy::test_pending_verdict_carries_per_policy_ask_timeout	failure	MAIN_POLICY_FIXTURE_KEYERROR_AG_TEST	no
tests.server.routes.test_sessions_policy::test_pending_verdict_registers_elicitation	failure	MAIN_POLICY_FIXTURE_KEYERROR_AG_TEST	no
tests.server.routes.test_sessions_policy::test_skill_slash_command_policy_body_uses_typed_command_text	failure	MAIN_POLICY_FIXTURE_KEYERROR_AG_TEST	no
tests.server.routes.test_sessions_snapshot::test_session_snapshot_publishes_skills_event_when_fetch_resolves	failure	MAIN_SNAPSHOT_SKILLS_PUBLISH	no
tests.server.routes.test_sessions_snapshot::test_session_snapshot_retries_503_model_options	failure	MAIN_SNAPSHOT_MODEL_OPTIONS_RETRY	no
tests.server.routes.test_sessions_snapshot::test_session_snapshot_retries_empty_model_options	failure	MAIN_SNAPSHOT_MODEL_OPTIONS_RETRY	no
tests.server.test_app::test_builtin_agent_id_is_stable_across_independent_stores	failure	ENV_BUNDLED_EXAMPLE_NOT_DIRECTORY	yes
tests.server.test_app::test_ensure_default_debby_agent_seeds_card	failure	ENV_BUNDLED_EXAMPLE_NOT_DIRECTORY	yes
tests.server.test_app::test_ensure_default_polly_agent_is_idempotent	failure	ENV_BUNDLED_EXAMPLE_NOT_DIRECTORY	yes
tests.server.test_app::test_ensure_default_polly_agent_no_churn_on_mtime_change	error	ENV_POLLY_RESOURCE_NOT_DIRECTORY	yes
tests.server.test_app::test_ensure_default_polly_agent_refreshes_on_spec_change	error	ENV_POLLY_RESOURCE_NOT_DIRECTORY	yes
tests.server.test_app::test_ensure_default_polly_agent_repairs_stale_cache	error	ENV_POLLY_RESOURCE_NOT_DIRECTORY	yes
tests.server.test_app::test_ensure_default_polly_agent_seeds_card	failure	ENV_BUNDLED_EXAMPLE_NOT_DIRECTORY	yes
tests.spec.test_debby_example::test_packaged_debby_resource_stays_in_sync_with_source_example	failure	ENV_BUNDLED_EXAMPLE_NOT_DIRECTORY	yes
tests.test_cursor_native_forwarder.TestCompactionCompletedForwarding::test_failed_completion_post_does_not_wedge_the_mirror	failure	MAIN_CURSOR_FORWARDER_STATE	no
tests.test_cursor_native_forwarder.TestCompactionCompletedForwarding::test_summary_blob_posts_compaction_completed_not_a_bubble	failure	MAIN_CURSOR_FORWARDER_STATE	no
tests.test_cursor_native_forwarder.TestForwardLoopPostFailures::test_connection_failure_retries_indefinitely	failure	MAIN_CURSOR_FORWARDER_STATE	no
tests.test_cursor_native_forwarder.TestForwardLoopPostFailures::test_long_blob_id_is_mirrored_not_wedged	failure	MAIN_CURSOR_FORWARDER_STATE	no
tests.test_cursor_native_forwarder.TestForwardLoopPostFailures::test_rejected_item_is_skipped_after_bounded_retries	failure	MAIN_CURSOR_FORWARDER_STATE	no
tests.testing.test_guardrails::test_empty_db_uri_skips_db_check[   ]	failure	MAIN_TEST_DB_GUARDRAIL_HEURISTIC	no
tests.testing.test_guardrails::test_empty_db_uri_skips_db_check[]	failure	MAIN_TEST_DB_GUARDRAIL_HEURISTIC	no
tests.testing.test_guardrails::test_looks_like_test_db_rejects_real_uris[sqlite:///contest.db]	failure	MAIN_TEST_DB_GUARDRAIL_HEURISTIC	no
tests.testing.test_guardrails::test_looks_like_test_db_rejects_real_uris[sqlite:///latest.db]	failure	MAIN_TEST_DB_GUARDRAIL_HEURISTIC	no
tests.testing.test_guardrails::test_looks_like_test_db_rejects_real_uris[sqlite:///test123.db]	failure	MAIN_TEST_DB_GUARDRAIL_HEURISTIC	no
tests.testing.test_guardrails::test_looks_like_test_db_rejects_real_uris[sqlite:///testing.db]	failure	MAIN_TEST_DB_GUARDRAIL_HEURISTIC	no
END_NODE_MAP
```

---

## 5.4 分类统计与结论

| category | groups | nodes |
|----------|-------:|------:|
| known_environment | 7 | 41 |
| known_flaky | 0 | 0 |
| known_main_code_failure | 23 | 85 |
| unclassified | 0 | 0 |

| eligible | count |
|----------|------:|
| yes | 41 |
| no | 85 |

**结论：`RELATIVE_PASS_EVIDENCE_INCOMPLETE`**

原因：存在 `known_main_code_failure` 和/或 `unclassified` 和/或 eligible=no 项；按 PRE_MERGE_GATES / 任务卡，这些 **不能** 仅因「main 也失败 / 集合相等」计入相对 PASS 的 known 环境/flaky 集合。最终 Gate 判定仍由 Codex 验收。

### 自检

命令（只读；未改 evidence）：

```text
python C:\Users\Administrator\gate1-evidence\triage_r6_selfcheck.py ^
  C:\Users\Administrator\gate1-evidence\20260729-1715-dc83140-grok-r6\baseline-fail-ids.txt ^
  F:\codex-ai\git项目部署\tmp\omnigent-review\docs\fixes\handoffs\GROK_COMPLETION_7_REWORK_5_TRIAGE.md
```

| 项 | 结果 |
|----|------|
| 退出码 | **0** |
| 标准输出 | **`TRIAGE_NODE_MAP_OK count=126`** |

统计复核：

| 指标 | 值 |
|------|-----|
| GROUP 数量（有映射） | 30 |
| known_environment nodes | 41（eligible yes） |
| known_flaky nodes | 0 |
| known_main_code_failure nodes | 85（eligible no） |
| unclassified nodes | 0 |
| eligible yes 合计 | 41 |
| eligible no 合计 | 85 |

---

## 禁止项遵守

- 未跑 pytest/Ruff/Gate/smoke
- 未改 r6 evidence / 旧 handoff / 源码
- 未 commit/push/merge/tag
- 未执行 Gate 2
