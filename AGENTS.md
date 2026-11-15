# Правила RoboHand.Simulator

Перед работой прочитай [docs/index.md](docs/index.md).

Решение владельца 08.11.2026: перед каждым техническим шагом сначала искать и применять готовый официальный/поддерживаемый workflow, CLI, asset/config hook или adapter. Фиксировать upstream commit и smallest smoke. Собственные pipeline, exporter, MCP-server, UI и orchestration framework не создавать без отдельного решения владельца после выявления точного gap.

Платформа — только EB300; SO-101 допустима как явно обозначенный reference example. Камера — Redmi 8A на запястье, концевики есть. Разработка через Codex; Hermes рассматривается отдельно как будущий task supervisor, а не motor controller.

[Полная политика](<../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/reuse-first-policy.md>). Стандартные CAD/URDF/config данные нашей механики допускаются; новый исполняемый adapter не считается готовым лишь по одинаковому интерфейсу.
