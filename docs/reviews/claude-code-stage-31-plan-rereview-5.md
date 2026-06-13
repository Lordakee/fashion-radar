The temp `/tmp/fashion-radar-example-config-stage31` approach is correct for the release-gate smoke:

1. It exercises the installed-wheel CLI against the public example CSV/JSON inputs using a real `scoring.yaml` filename, matching the runtime CLI contract.
2. Copying `configs/scoring.example.yaml` to `/tmp/.../scoring.yaml` avoids dirtying the repository and does not imply the product generates runtime config files.
3. It remains compatible with an sdist package-content check for `configs/scoring.example.yaml`; the smoke consumes the public example config as an operator-prepared runtime config, while the package check separately verifies the example file is shipped.
4. I do not see new Critical or Important issues from this change.

APPROVED FOR STAGE 31 RELEASE GATE
