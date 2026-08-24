---
title: CIS 설정
description: CIS workflow, output location, agent behavior를 설정합니다
---

Creative Intelligence Suite workflow, output 동작, agent preference를 설정합니다.

## 설정 파일

CIS 설정은 다음 위치에 저장됩니다.

```
_bmad/cis/config.yaml
```

파일이 없으면 CIS는 기본값을 사용합니다.

## 설정 옵션

| 설정 | 설명 | 기본값 |
| ------- | ----------- | ------- |
| **output_folder** | workflow output을 저장할 위치 | `./_bmad-output/` |
| **user_name** | workflow 진행에서 사용할 이름 | `User` |
| **communication_language** | agent 응답 언어 | `english` |

### output_folder

**workflow 결과를 저장할 위치입니다.**

절대 또는 상대 경로입니다. workflow output은 `{workflow-name}-{date}.md`로 이름을 붙입니다.

**예시:**

```yaml
output_folder: "./creative-outputs"
# 또는
output_folder: "/Users/name/Documents/creative-work"
```

**상대 경로**는 project root에서 해석합니다.

### user_name

**진행 중 agent가 사용자를 부르는 방식입니다.**

개인화된 interaction에 사용합니다. agent는 응답에 사용자의 이름을 넣습니다.

**예시:**

```yaml
user_name: "Alex"
# Carson은 다음과 같이 말할 수 있습니다: "Alex, 다른 각도를 시도해 봅시다..."
```

### communication_language

**workflow 진행에 사용할 언어입니다.**

agent는 고유한 성격을 유지하면서 지정한 언어로 대화합니다.

**지원 값:**

- `english` (기본값)
- `spanish`
- `french`
- `german`
- `italian`
- `portuguese`

**예시:**

```yaml
communication_language: "spanish"
# Maya가 재즈 같은 style을 유지하면서 스페인어로 진행합니다
```

## 기본 설정

설정 파일이 없으면 CIS는 다음을 사용합니다.

```yaml
output_folder: "./_bmad-output/"
user_name: "User"
communication_language: "english"
```

## 설정 만들기

`_bmad/cis/config.yaml`을 만들거나 편집합니다.

```yaml
# CIS 설정

output_folder: "./_bmad-output/"
user_name: "Your Name"
communication_language: "english"
```

## Workflow별 문맥

일부 workflow는 command-line flag로 추가 문맥을 받습니다.

### Context data 제공

workflow에 context document를 전달합니다.

```bash
workflow design-thinking --data /path/to/user-research.md
workflow innovation-strategy --data /path/to/market-analysis.md
workflow problem-solving --data /path/to/problem-brief.md
workflow storytelling --data /path/to/brand-guidelines.md
```

context file은 Markdown이어야 합니다. agent는 이 정보를 진행에 반영합니다.

## 환경 변수

CIS는 다음 환경 변수를 따릅니다.

| 변수 | 목적 | 예시 |
| ---------- | ------- | ------- |
| `BMAD_OUTPUT_DIR` | output folder override | `BMAD_OUTPUT_DIR=./outputs` |
| `BMAD_USER_NAME` | user name override | `BMAD_USER_NAME=Jordan` |
| `BMAD_LANGUAGE` | language override | `BMAD_LANGUAGE=spanish` |

환경 변수는 설정 파일보다 우선합니다.

## 설정 문제 해결

### Output이 나타나지 않음

output folder path가 유효한지 확인합니다.

```bash
# path resolution 시험
ls ./_bmad-output/
```

folder가 존재하거나 CIS가 만들 수 있는지 확인하세요.

### Agent가 이름을 사용하지 않음

`_bmad/cis/config.yaml`의 `user_name`이 올바른지 확인합니다.

### 언어가 바뀌지 않음

`communication_language`가 지원 값을 사용하는지 확인합니다. custom language는 agent prompt update가 필요합니다.

## 다음 단계

- **[Getting Started](/tutorials/getting-started.md)** — 기본 설정으로 workflow 사용
- **[Workflows Reference](/reference/workflows.md)** — 자세한 workflow 기제

