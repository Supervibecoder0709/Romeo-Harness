원문: agent-skills/codex/publish-project-to-github/SKILL.md  
고정 근거: [E09]

---
name: publish-project-to-github
description: 완성된 local project를 의도적인 GitHub repository로 package하고, 강한 README와 visual preview를 만들고, 안전하게 push하고, 호환되는 경우 public GitHub Pages URL을 설정하고, deployed result를 verify한다. local HTML/CSS/JavaScript experiment나 small web project를 upload, publish, open-source, share하거나 live demo가 있는 documented GitHub repository로 만들라는 요청에 사용한다.
---

# GitHub에 프로젝트 발행

완성된 local project를 깨끗한 public artifact로 바꾼다. repository 생성, public visibility, deployment를 별도 gate로 다룬다. push 성공은 public site가 작동한다는 proof가 아니다.

## Deliverable

적용 가능한 항목을 만든다.

- 범위가 좁은 Git repository
- 의도적인 public 또는 private GitHub repository
- project-specific README.md
- visual project일 때 실제 preview image
- 가치가 있을 때 portable build 또는 remix prompt
- 호환되는 web project의 configured GitHub Pages site
- push 이후 및 deploy 이후 read-back

## 1. Scope와 authority 확정

write 전에 local project, repository state, remote, local instruction을 검사한다.

다음을 확인하거나 안전하게 추론한다.

- 정확한 project directory와 의도한 file
- repository name과 owner
- target이 public인지 private인지
- existing repository를 update할지 new repository를 만들지
- live website, source hosting만, 또는 둘 다 원하는지

사용자가 public sharing, public URL, open source 또는 동등한 것을 명시적으로 요청할 때만 public repository 생성을 승인한다. 그렇지 않으면 생성 전 visibility를 질문한다.

명확한 authorization 없이 force-push, existing remote overwrite, repository visibility 변경, existing Pages configuration 교체를 하지 않는다.

## 2. Packaging 전 audit

project root에서 bundled audit를 실행한다.

~~~bash
bash /path/to/publish-project-to-github/scripts/audit_public_project.sh .
~~~

그 다음 script를 판단의 대체물로 취급하지 말고 finding을 검사한다.

다음이 있으면 publication을 block한다.

- API key, token, private key, password, .env file
- personal data 또는 private client information
- runtime에 필요한 absolute local filesystem path
- unlicensed 또는 private asset
- 누락된 runtime file
- 이미 존재하는 repository name의 불명확한 ownership

모든 external runtime URL과 generated asset을 review한다. 필요한 network dependency는 README에 적는다.

발행 전 existing license를 검사한다. 사용자가 다른 사람의 재사용/수정을 명시적으로 원하고 license가 없으면 임의로 넣지 말고 어떤 license를 더할지 물어본다. public viewing만이 목적이면 license 부재가 deployment를 막지는 않지만 reuse right가 명시적으로 부여되지 않았음을 보고한다.

## 3. Packaging model 선택

### Clean existing repository

remote, history, tracked file이 의도한 public project와 맞으면 existing checkout을 사용한다. 요청한 file만 stage한다.

### Mixed 또는 unrelated workspace

source workspace에 unrelated experiment, deletion, private file, history가 있으면 clean project directory 또는 sibling checkout을 만든다. 의도한 runtime file만 복사한다. 편의를 위해 mixed folder 전체를 publish하지 않는다.

### Existing public repository

변경 전 default branch, Pages source, README, license, remote state를 검사한다. 의도적으로 pull 또는 reconcile하며 force push로 divergence를 숨기지 않는다.

정적 one-file experiment에는 다음 최소 shape를 선호한다.

~~~text
project-name/
├── index.html
├── README.md
├── PROMPT.md        # 선택
├── assets/          # 선택: preview 또는 runtime asset
└── .gitignore
~~~

## 4. Repository presentation 구축

README를 실제 project에서 작성한다. assets/README-template.md는 시작 구조로만 쓰고 final copy로 쓰지 않는다.

다음을 포함한다.

- project name과 experience를 설명하는 구체적인 한 문장
- 상단의 live demo link와, GitHub 밖에서도 유용하면 repository source link
- 실제 실행 project에서 capture한 screenshot 또는 짧은 GIF
- 핵심 interaction 또는 feature
- architecture와 특별한 implementation choice의 간결한 설명
- 정확한 local run instruction
- project structure
- runtime dependency와 network requirement
- reference가 영감을 줬다면 originality, attribution, non-affiliation note

agent-built project에는 관련 coding agent로 rebuild/remix하는 portable prompt와 공식 link를 선택적으로 더한다. 발행 전 current official URL을 확인한다.

cutting-edge, stunning, production-ready 같은 일반 claim을 피한다. 구체적인 craft와 behavior를 선호한다.

## 5. Local verify

module-based site를 disk에서 직접 여는 대신 project의 실제 runtime을 사용한다.

정적 site의 경우:

~~~bash
python3 -m http.server 4173 --bind 127.0.0.1
~~~

다음을 점검한다.

- initial render
- primary interaction path
- primary interaction의 return, close, recovery path
- responsive이면 일반 desktop viewport와 약 390 × 844 narrow viewport
- 모든 README run command
- missing file과 404
- console error와 warning
- project-name 같은 repository subpath 아래의 relative URL

사용자가 요청했거나 repository instruction이 요구하는 browser를 사용한다. README preview는 이 verified runtime에서 capture한다.

## 6. Commit과 repository 생성

GitHub CLI와 authenticated session이 필요하다.

~~~bash
gh --version
gh auth status
~~~

생성 전 name availability를 확인한다.

~~~bash
gh repo view OWNER/REPOSITORY
~~~

의도한 package만 initialize하고 commit한다.

~~~bash
git init -b main
git add -- README.md index.html .gitignore
git diff --cached --check
git commit -m "Publish PROJECT_NAME"
~~~

mixed tree에서는 git add -A로 넓히지 말고 optional file을 명시적으로 추가한다.

audit와 local verification이 pass한 뒤에만 create/push한다.

~~~bash
gh repo create OWNER/REPOSITORY \
  --public \
  --source=. \
  --remote=origin \
  --push \
  --description "CONCRETE_DESCRIPTION"
~~~

public visibility가 승인되지 않았다면 private를 사용한다. repository가 이미 있으면 recreate하지 않고 remote를 명시적으로 설정하고 push한다.

## 7. Public site 설정

Pages를 활성화하기 전 project를 분류한다.

- **Static root**: main과 /를 publish.
- **Static docs folder**: main과 /docs를 publish.
- **Framework build**: framework가 지원하는 Pages output과 현재 공식 GitHub Actions guidance를 사용.
- **Server, database, private runtime**: GitHub Pages와 호환되지 않는다. blocker를 설명하고 사용자 authorization이 있을 때만 다른 host를 선택.

Pages settings를 바꾸기 전 references/github-pages.md를 읽는다. resulting public URL을 repository homepage에 설정하고 작고 정확한 discovery topic set을 추가한다.

## 8. External state verify

모든 external change를 read back한다.

~~~bash
gh repo view OWNER/REPOSITORY \
  --json nameWithOwner,url,visibility,description,homepageUrl,defaultBranchRef

gh api repos/OWNER/REPOSITORY/pages
gh api repos/OWNER/REPOSITORY/pages/builds/latest
~~~

Pages build가 built를 보고하거나 구체적으로 fail할 때까지 기다린다. 그 다음 public URL을 열어 다음을 확인한다.

- 최종 HTTPS URL에서 HTTP navigation 성공
- 기대한 project UI가 보임
- representative interaction 하나가 main application state를 바꾸고 clean하게 return 또는 close
- asset이 repository subpath 아래에서 resolve
- browser error나 warning 없음
- README link resolve

요청 deliverable이면 public page를 사용자를 위해 열어 둔다.

## 9. 정확한 결과 handoff

다음을 반환한다.

- repository URL
- 생성했다면 public site URL
- commit과 branch
- Pages build status
- 실제 실행한 check
- 남은 dependency, licensing, deployment limitation

pushed, Pages configured, Pages built, live site verified를 구분한다. 하나의 성공으로 뭉개지 않는다.

## Failure 규칙

- unrelated dirty work와 history를 보존한다.
- secret이 commit되었다면 push 전에 history에서 제거하고 secret을 publish하지 않는다.
- local context로 GitHub owner 또는 existing repository target을 확인할 수 없으면 추측하지 않는다.
- file URL preview가 GitHub Pages compatibility를 증명한다고 주장하지 않는다.
- 성공한 CLI exit를 external write의 유일한 verification으로 쓰지 않는다.
- GitHub Pages가 호환되지 않을 때 다른 host로 조용히 대체하지 않는다.

## Resource

- package 전 scripts/audit_public_project.sh를 실행한다.
- Pages 설정/디버깅 전 references/github-pages.md를 읽는다.
- assets/README-template.md를 복사하고 실제 project evidence로 모든 placeholder를 다시 쓴다.
