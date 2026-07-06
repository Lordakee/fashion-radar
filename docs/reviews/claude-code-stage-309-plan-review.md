Now I have everything I need. Here is the review.

---

## Verdict

**Approve with Important fixes.**

The plan is well-scoped, architecturally correct, and respects all stated boundaries. Three issues need fixing before implementation: one will cause a test to fail with the correct implementation (critical), one introduces a naming mismatch that will likely create a duplicate helper (important), and one uses a `uv` invocation that contradicts the project's frozen/no-config discipline (important). The clustering key is narrower than it looks and that assumption should be
