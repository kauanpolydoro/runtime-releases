# ruff: noqa: PLR2004, S101

import runpy
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
WORKFLOW = (REPOSITORY / ".github" / "workflows" / "publish-download.yml").read_text(
    encoding="utf-8"
)


def test_only_trusted_default_branch_events_can_publish() -> None:
    trigger = WORKFLOW.split("on:\n", 1)[1].split("\npermissions:", 1)[0]

    assert "schedule:" in trigger
    assert "workflow_dispatch:" in trigger
    assert "push:" not in trigger
    assert "workflow_run:" not in trigger
    assert "permissions:\n  contents: read" in WORKFLOW
    assert WORKFLOW.count("permissions:\n      contents: write") == 2
    assert "cancel-in-progress: false" in WORKFLOW


def test_transport_is_isolated_pinned_and_revalidated() -> None:
    assert "https://github.com/kauanpolydoro/runtime-release-inbox.git" in WORKFLOW
    assert WORKFLOW.count("repository: kauanpolydoro/runtime-release-inbox") == 2
    assert "ref: ${{ needs.discover.outputs.candidate_sha }}" in WORKFLOW
    assert "ref: ${{ needs.discover.outputs.promotion_sha }}" in WORKFLOW
    assert WORKFLOW.count("persist-credentials: false") == 2
    assert "Validate immutable candidate package" in WORKFLOW
    assert "Validate pilot attestation and candidate identity" in WORKFLOW
    assert WORKFLOW.count("require_newer_semver.py") >= 4
    assert "openssl pkeyutl -verify" in WORKFLOW
    assert "git -C trusted push" not in WORKFLOW
    assert "already contains the same immutable assets" in WORKFLOW
    assert "already_promoted=$already_promoted" in WORKFLOW
    assert "if: steps.promotion.outputs.already_promoted != 'true'" in WORKFLOW
    assert "actions/checkout@v4" not in WORKFLOW


def test_old_abandoned_candidate_cannot_be_promoted() -> None:
    gate = REPOSITORY / ".github" / "scripts" / "require_newer_semver.py"
    gate_main = runpy.run_path(str(gate))["main"]

    assert gate_main([str(gate), "0.1.50", "v0.1.49"]) == 0
    assert gate_main([str(gate), "0.1.49", "v0.1.49"]) == 1
    assert gate_main([str(gate), "0.1.48", "v0.1.49"]) == 1
    promotion = WORKFLOW.split("- name: Promote the same bytes to stable", 1)[1]
    assert promotion.index("require_newer_semver.py") < promotion.index(
        "gh release edit"
    )


if __name__ == "__main__":
    test_only_trusted_default_branch_events_can_publish()
    test_transport_is_isolated_pinned_and_revalidated()
    test_old_abandoned_candidate_cannot_be_promoted()
