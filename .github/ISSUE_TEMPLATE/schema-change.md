---
name: Schema change proposal (C-level)
about: Propose a C-level schema change (new kind/form/source-types enum value, new facet field, new top-level domain, or subject deprecation).
title: "[schema] "
labels: schema-change
assignees: daehyeonxyz
---

## 중요 안내 (Important)

C-level 스키마 변경은 PR로 직접 추가할 수 없습니다.
이 issue에서 제안하면, 메인테이너가 `.naite/ontology/facets.json`, `subject-tree.md` 등을 직접 수정합니다.

(C-level schema changes must NOT be added directly in a PR.
The maintainer will make the change to `.naite/ontology/facets.json`, `subject-tree.md`, etc. after review.)

C 등급(내부 기준 'user decision')은 외부 기여자에게는 메인테이너가 소유자 결정을 집행하는 형태로 적용됩니다. 외부 기여자는 PR로 `.naite/ontology/facets.json` 을 직접 편집하지 않습니다 (core enum 변경은 C-level 메인테이너 결정; user kind 선언은 vault 소유자 행위로, 공유 하네스 repo의 PR 범위가 아닙니다).

C-level 범위: 새 `kind`/`form`/`source-types` enum 값, 새 facet 필드, 새 top-level domain, subject deprecation.
참고: `docs/CONVENTIONS.md § Schema evolution` (Level C 행).

---

## 무엇을 추가/변경하려 하나요? (What to add or change?)

<!-- 예: 새 kind 값 `tutorial`, 새 facet `difficulty`, `ml/optimization` subject deprecation 등 -->

## 왜 필요한가요? (Why is this needed?)

<!-- 어떤 페이지 또는 콘텐츠 패턴이 현재 스키마로 표현하기 어려운지 설명해 주세요. -->

## 영향 받는 페이지 (Affected pages)

<!-- 이 변경이 적용되면 업데이트가 필요한 기존 페이지가 있나요? 몇 개나 되나요? -->

## 대안 (Alternatives considered)

<!-- 기존 `kind`/`form`/`topics`/`subject`를 활용해서 표현할 수 있는 방법이 있나요? 없다면 왜 불충분한지 설명해 주세요. -->

## 하위 호환성 (Backward compatibility)

<!-- 이 변경이 기존 harness-lock, lint-ontology, naite-app 파서에 영향을 주나요? -->
