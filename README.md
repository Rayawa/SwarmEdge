# SwarmEdge

English | [简体中文](README_zh.md)


Exploring device-edge-cloud collaboration, peer-to-peer cluster communication, and on-device NPU inference.

SwarmEdge is a research project at the problem-definition and direction-exploration stage, studying the combination of device-edge-cloud collaboration, communication between cluster nodes and on-device NPU inference.

**Current status: exploratory research.** The repository contains research notes and historical drafts, without an implemented, deployable cluster system. Application scenarios and specific research questions remain to be defined.

## Main Research Directions

| Direction | Research Focus |
| --- | --- |
| Device-edge-cloud integration | Consider device, edge and cloud as a whole and study how their responsibilities and collaboration support a concrete task. |
| Communication between cluster nodes | Explore direct information exchange and collaboration between nodes, in addition to host-to-node communication. |
| Node-side NPU inference | Explore local inference on end nodes and its relationship to overall task coordination. |

These are proposed directions; concrete contributions need to emerge through problem definition and experimental validation.

## Candidate Technology Base

- **Device side**: OpenHarmony.
- **On-device inference**: Ascend NPU and CANN.
- **Host side**: potentially openEuler.

These are technology intentions. Board selection, system versions and the compatibility of OpenHarmony with CANN still need verification.

## Open Questions

1. Which concrete task needs device-edge-cloud collaboration, peer-node communication and local inference together?
2. How should that task determine layer responsibilities, node types and communication mechanisms?
3. What measurable value could the combined design add compared with existing approaches?
4. Which baselines, data and experimental metrics should evaluate it?

Application scenarios, node counts, models, algorithms, budgets and acceptance criteria are not yet fixed.

## Repository Structure

```text
SwarmEdge/
├── README.md
└── archive/
    └── 2026-10-20_早期方案_未采纳/
```

## Historical Proposals and References

Earlier scenario, architecture, algorithm, budget, execution and acceptance drafts, together with research material, are retained in the [early-proposal archive](archive/2026-10-20_早期方案_未采纳/归档说明.md).

The archive supports traceability and reference. Its proposals, assumptions and conclusions are not current decisions and do not establish completed implementation or validation.

## Obtain the Project

```bash
git clone https://github.com/Rayawa/SwarmEdge.git
cd SwarmEdge
```

There is currently no runtime to install or application to launch. Read this page first, then consult the archived material as needed.

## Sources and Licensing

Rights to cited literature and third-party material remain with their authors or rights holders. No additional repository-wide open-source license is granted.
