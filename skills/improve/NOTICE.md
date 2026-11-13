# Notice

This skill is adapted from [`improve`](https://github.com/shadcn/improve) by shadcn.
The advisor and executor split, the hard rules, the audit categories, the plan
template, and the execute, reconcile, and issues flows derive from that work.

The original is distributed under the MIT License:

```text
MIT License

Copyright (c) 2026 shadcn

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Changes in this version: the workflow is restructured for progressive loading;
audit depth is separate from effort; findings are vetted and, for HIGH-impact
bugs, reproduced in a scratch copy; plans gain a generated-files scope, a
failing-test-first rule (a mutation check for test-only plans), exact excerpts
checked against the stamped commit, and a report format; `execute` can dispatch
through the `delegate` skill and checks scope and test gaming during review; Go
and go-sphere notes are added; and `scripts/plans.py` lints plans and reports
drift, merge state, and scope.
