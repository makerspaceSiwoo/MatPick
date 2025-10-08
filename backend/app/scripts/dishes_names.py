import os, re, sys
import pdfplumber
from sqlalchemy import create_engine, text

# 머리글/라벨(완전 제외)
HEADER_KEYWORDS = [
    "음식의 분류",
    "음식군",
    "음식명",
    "No 음식명",
    "No",
    "빵, 과자류",
]

# 식사와 거리가 먼 카테고리(키워드 기반 제외)
DENY_KEYWORDS = [
    # 과자/빵/디저트/패스트리
    "도우넛",
    "도넛",
    "롤빵",
    "식빵",
    "베이글",
    "머핀",
    "케이크",
    "파이",
    "크로쌍",
    "패스트리",
    "비스켓",
    "쿠키",
    "크래커",
    "웨하스",
    "샌드",
    "샌드위치",
    "토스트",
    "와플",
    "파운드",
    # 과자·스낵·시리얼
    "스낵",
    "과자",
    "칩",
    "초코",
    "쵸코",
    "프링글",
    "콘칩",
    "콘푸로스트",
    "시리얼",
    # 유제품/디저트류
    "우유",
    "요구르트",
    "치즈",
    "푸딩",
    "커스터드",
    "아이스크림",
    "쉐이크",
    "빙수",
    # 음료/주류/차/커피
    "주스",
    "쥬스",
    "음료",
    "콜라",
    "사이다",
    "환타",
    "에이드",
    "이온음료",
    "코코넛수",
    "맥주",
    "소주",
    "와인",
    "위스키",
    "브랜디",
    "칵테일",
    "진",
    "럼",
    "보드카",
    "막걸리",
    "청주",
    "차",
    "커피",
    "라떼",
    "코코아",
    # 장아찌/젓갈/양념
    "장아찌",
    "피클",
    "젓",
    "젓갈",
    "소스",
    "드레싱",
    "식초",
    "가루",
    "분말",
    "다시다",
    "시럽",
    # 이유식
    "이유식",
    "유아용과자",
    # 단일 식품(생과일/채소/견과·해조/가공 전 재료)
    "생것",
    "말린것",
    "건조칩",
    "통조림",
    "가공품",
    "가공식품",
    "사과",
    "바나나",
    "딸기",
    "오렌지",
    "포도",
    "자몽",
    "키위",
    "수박",
    "멜론",
    "망고",
    "블루베리",
    "복숭아",
    "배",
    "체리",
    "상추",
    "양배추",
    "오이",
    "토마토",
    "파프리카",
    "당근",
    "감자",
    "고구마",
    "버섯",
    "견과",
    "호두",
    "아몬드",
    "땅콩",
    "김",
    "미역",
    "다시마",
]

# 허용(식사성) 키워드: DENY에 걸려도 이게 포함되면 살림
ALLOW_KEYWORDS = [
    "밥",
    "덮밥",
    "국밥",
    "비빔밥",
    "볶음밥",
    "라이스",
    "리조또",
    "빠에야",
    "면",
    "국수",
    "라면",
    "우동",
    "냉면",
    "파스타",
    "스파게티",
    "짜장면",
    "짬뽕",
    "쫄면",
    "칼국수",
    "쌀국수",
    "국",
    "탕",
    "찌개",
    "전골",
    "수제비",
    "죽",
    "스프",
    "구이",
    "볶음",
    "조림",
    "튀김",
    "전",
    "부침",
    "찜",
    "수육",
    "샤브",
    "불고기",
    "두루치기",
    "잡채",
    "떡볶이",
    "김밥",
    "초밥",
    "카레",
    "돈까스",
    "스테이크",
    "피자",
    "핫도그",
    "버거",
    "타코",
    "분짜",
    "쌈",
    "비빔",
]

# "숫자 + 음식명" 패턴을 한 줄에서 연속으로 캡처
PAIR_RE = re.compile(r"\b(\d+)\s*([^\d\n]+?)(?=(?:\s+\d+\s*|$))")


def is_header_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return True
    for kw in HEADER_KEYWORDS:
        if kw in s:
            return True
    # 단독 섹션 라벨(예: '빵, 과자류', '밥류' 등 짧은 라벨)도 스킵
    if len(s) <= 8 and ("류" in s or "," in s):
        return True
    return False


def clean_name(name: str) -> str:
    # 불필요 구두점·공백 정리
    n = re.sub(r"\s+", " ", name).strip(" ,.;()[]")
    # 너무 짧거나 숫자만인 항목 제거
    if len(n) < 2 or re.fullmatch(r"\d+", n):
        return ""
    # 열제목/잡텍스트 방지
    if n in ("음식명", "음식군", "No"):
        return ""
    return n


def deny_by_keywords(n: str) -> bool:
    has_deny = any(k in n for k in DENY_KEYWORDS)
    has_allow = any(k in n for k in ALLOW_KEYWORDS)
    return has_deny and not has_allow


def extract_names(pdf_path: str):
    names = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            txt = page.extract_text() or ""
            for line in txt.splitlines():
                if is_header_line(line):
                    continue
                for m in PAIR_RE.finditer(line):
                    raw = clean_name(m.group(2))
                    if not raw:
                        continue
                    if deny_by_keywords(raw):
                        continue
                    names.append(raw)

    # 중복 제거(공백·대소문자 무시)
    seen, out = set(), []
    for n in names:
        key = re.sub(r"\s+", " ", n.lower())
        if key not in seen:
            seen.add(key)
            out.append(n)
    return out


def main(pdf_path: str):
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("환경변수 DATABASE_URL 이 필요합니다.")
        sys.exit(2)
    engine = create_engine(db_url, pool_pre_ping=True)

    data = extract_names(pdf_path)
    if not data:
        print("추출 결과가 비었습니다.")
        return

    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS dishes_name_unique_idx ON dishes ((lower(name)));"
            )
        )
        ins = text("INSERT INTO dishes (name) VALUES (:name) ON CONFLICT DO NOTHING;")
        inserted = 0
        for nm in data:
            r = conn.execute(ins, {"name": nm})
            inserted += r.rowcount or 0

    print(f"총 후보: {len(data)} / 신규 삽입: {inserted} / 스킵: {len(data)-inserted}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python dishes_names.py <input.pdf>")
        sys.exit(1)
    main(sys.argv[1])
