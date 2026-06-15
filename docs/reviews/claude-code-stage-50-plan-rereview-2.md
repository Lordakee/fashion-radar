## Critical findings

None found.

## Important findings

None found.

The prior remaining Important finding is addressed. The plan now adds direct `ManualSignalRow` validation checks for:

- omitted `source_weight` defaults to `1.0`;
- blank `source_weight` defaults to `1.0`;
- `source_weight=5` is accepted;
- `source_weight=0` is rejected;
- `source_weight=5.1` is rejected.

This covers the requested parity with the existing importer model, not only the profile/schema/default metadata.

## Minor findings

1. **Profile strictness test still uses manual `try`/`except` instead of `pytest.raises`**

   The prior Minor suggestion remains only partially addressed. The plan imports `pytest`, but `test_profile_model_rejects_extra_fields_and_missing_required_fields` still uses manual `try`/`except` assertions.

   This is not blocking; the test is functionally correct. If desired, it can be simplified with:

   ```python
   with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
       CommunitySignalProducerProfile.model_validate(with_extra)

   with pytest.raises(ValidationError, match="Field required"):
       CommunitySignalProducerProfile.model_validate(without_contract_version)
   ```

2. **Release-review prompt says no account/session/cookie handling, while implementation docs mention cookies only as unsupported/prohibited**

   This is acceptable because the wording is negative/boundary-oriented and `cookie` is also a valid prohibited field. During implementation, keep all such references clearly framed as “not supported,” “prohibited,” or “does not store/use cookies.”

## Missing tests or verification gaps

No blocking gaps found.

The added plan coverage now includes the previously requested hardening:

- direct `ManualSignalRow` `source_weight` bound/default checks;
- unexpected positional path argument rejection without artifacts;
- installed-wheel `community-signal-profile --format json` smoke from a temporary cwd;
- installed-wheel no-artifact assertions for config/data/reports and common SQLite/report/digest outputs.

One optional extra hardening test, not required for approval:

- Add a real-process unexpected positional argument check, mirroring the `CliRunner` positional rejection test. The existing `CliRunner` test is sufficient for the plan boundary, but a subprocess variant would further lock CLI packaging behavior.

## Scope creep risks

1. **Recommended commands include import/review workflow commands**

   Still acceptable because they are printed as guidance only. Implementation must not inspect, validate, execute, or derive anything from those paths or commands.

2. **Docs mention external tools and community producers**

   Acceptable as long as wording stays limited to user-controlled local tools that generate sanitized handoff CSV/JSON. Avoid implying source discovery, platform monitoring, platform API integration, ranking, demand proof, or compliance certification.

3. **Potential temptation to derive profile values by reading files at runtime**

   The design correctly keeps runtime print-only. Tests may read schema/examples, but the `community-signal-profile` command itself should not read handoff files, examples, schema files, directories, SQLite, config, data, or reports.

4. **Future drift between schema/examples/importer/profile**

   The proposed tests strongly mitigate this by binding the profile to the CSV header, JSON schema properties, existing constants, `ManualSignalRow` source-weight behavior, and the checked-in profile example.

## Approval status for implementation

**Approved for implementation.**

The prior Important finding is resolved, the hard boundaries are preserved, and the added no-artifact/positional-argument/installed-wheel verification is sufficient. The remaining notes are minor or optional hardening only.
