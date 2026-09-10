# Verification record

Verified locally on September 9, 2026 using Python 3.14.7, SciPy 1.18.0, and Matplotlib 3.11.1 on macOS.

- Existing suite: 17 tests passed (`python -m unittest -v test_main`).
- Main example: 5 suppliers, 8 customers, 40 variables; objective 1530; baseline validation passed.
- Supplier B at 50% capacity loss: objective 1565; increase 35 / approximately 2.29%.
- Stress test: 25 scenarios; complete losses of A and D reported infeasible.
- Binding baseline capacities: C and E.
- Both PNGs regenerated from the existing program using the noninteractive Agg backend.
- Small regression fixture: objective 580, asserted by the existing test.

The original project brief stated 12 tests; the provided source contains 17. The source directly imports SciPy and Matplotlib, not NumPy. Documentation reflects the supplied implementation. Code and CSV files were not changed for publication.

A review of the supplied source, CSVs, documentation, and output images found no obvious credentials or private records. No `.git` directory was supplied, so historical commits could not be audited. This is a limited inspection, not a guarantee that no vulnerability exists.

The publication copy omits the local virtual environment, Python caches, and a zero-byte placeholder file. The original local folder is preserved. No license was added.
