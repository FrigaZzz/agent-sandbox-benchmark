# Cheaper AI. What about the machines?

Readable companion to the nine-page PDF.

## 1. Cheaper AI, what about the machines?

Cheaper AI. What about the machines?

Why I revisited agent sandboxes.

MODEL

instructions

MACHINE

execution

RESULT

verified output

Cost, privacy, features and customization.


## 2. The news that reopened the choice

New sandboxes. Architecture rethink.

GOOGLE / 9 SEPTEMBER 2026

Shell + computer-use sandboxes reach GA. Pause idle compute while preserving files.

Source: [Google release](https://docs.cloud.google.com/gemini-enterprise-agent-platform/release-notes#September_09_2026)

DATABRICKS / 16 JUNE 2026

Sandbox announced within Agent Bricks. Dedicated offering currently no-charge Beta.

Source: [Databricks news](https://www.databricks.com/blog/agent-bricks-dais-2026)

These developments prompted my side-project architecture review, mainly around cost. New features aren't benchmark results.


## 3. State is three contracts

What survives?

Files, durable disk and memory are separate promises.

01

BETWEEN CALLS

Can the next call read the files?

02

AFTER STOP

Does disk remain? For how long?

03

ON RESUME

Are variables and processes restored?

E2B documents memory + files on default pause. Our E2B/Modal checks verified files across calls.

Stop/resume was not tested in this pilot.

Source: [E2B persistence](https://docs.e2b.dev/sandbox/persistence.md)


## 4. Image and hardware

Bring your tools. Choose the hardware.

IMAGE

Libraries and toolchain

ALLOCATION

CPU, RAM and device

E2B

Templates; CPU-only sandboxes.

MODAL

GPU offered; plan for interruptions.

DAYTONA

Shared GPU placement ignores preference.

Check the exact runtime class and controls. GPU configurations were not benchmarked here.

Source: [E2B GPU FAQ](https://docs.e2b.dev/faq/gpu-support.md)

Source: [Modal resources](https://modal.com/docs/guide/sandbox-resources)

Source: [Daytona regions](https://www.daytona.io/docs/en/regions.md)


## 5. The whole data map

An EU region is one part of the map.

MODAL EXAMPLE / DOCUMENTED DATA LOCATIONS

COMPUTE EEA-pinned

EEA is broader than the EU. Pinning covers compute.

LOGS

US stdout / stderr

SNAPSHOTS

US, when created

MANAGED STORAGE

US durable products

Also trace backups, control-plane data, support access and model calls. A model endpoint has its own processing boundary.

Source: [Modal residency](https://modal.com/docs/guide/data-residency)


## 6. Two different economic trends

The machines have their own economics.

CHEAPER ACCESS TO CAPABILITY

280-fold+

GPT-3.5-level inference cost drop. Nov 2022 to Oct 2024 (Stanford AI Index).

2026 INFRASTRUCTURE PRICE PRESSURE

Server memory supply remains tight. TrendForce forecasts further price rises. Hetzner raised new-order cloud prices in June.

These are different markets and time periods.

Source: [Stanford AI Index](https://hai.stanford.edu/ai-index/2025-ai-index-report)

Source: [Memory forecast](https://www.trendforce.com/presscenter/news/20260930-13258.html)

Source: [Hetzner prices](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/#cloud-servers)


## 7. Economics

Cheaper tokens. Still a machine bill.

Same model budget. Different billed running time. Hypothetical USD usage, before credits.

MODEL-AGNOSTIC SCENARIO / NOT A MODEL RATE

Assumed model budget: $0.003 in both

E2B: 2 VCPU + 4 GIB / BILLED RUNNING TIME

10 seconds

$0.00046

5 minutes

$0.01380

Either bill can dominate. Count the whole job. Sandbox storage included; paid fees, tax, retries and other service charges excluded.

Replace with your model bill

Source: [E2B pricing](https://e2b.dev/pricing)


## 8. Five questions worth asking

Five questions worth asking.

01

What survives between calls, after a stop and on resume? Files, disk, memory.

02

Does a custom image also reserve a GPU? It doesn't. Request hardware separately.

03

Where do logs, backups and model calls live? Map every data surface and access path.

04

What happens when a request times out? Verify cancellation and recovery.

05

What's the cost per verified completion? Keep credits apart from gross usage.

Gross campaign cost / verified completed tasks


## 9. Why I built and shared the benchmark

A benchmark for my next decision.

File/data checks produced the expected results with E2B, Modal and Google's default code. The tested setups give me a starting shortlist.

THE DEEP DIVE

Article: architecture, costs and provider trade-offs.

Repository: exact setups, workload checks and retained results.

Theo: cheaper capability can enable more work. Article + repository links in the post.

Source: [Theo's video](https://www.youtube.com/watch?v=vRS2leJLAI0)
