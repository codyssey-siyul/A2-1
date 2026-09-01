import os
import json
import base64

from dotenv import load_dotenv
from openai import OpenAI
import matplotlib.pyplot as plt


# ============================================================
# 1. 환경 설정 및 API 키 확인
# ============================================================

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("🚨 에러: .env 파일에 OPENAI_API_KEY가 없습니다!")
    print("   .env 파일에 OPENAI_API_KEY=발급받은_API_KEY 형식으로 입력해주세요.")
    exit()

client = OpenAI(api_key=api_key)


# ============================================================
# 2. 브랜드 요소 생성
# ============================================================

def generate_brand_identity(brief_data):
    """
    LLM API를 호출하여
    네이밍, 슬로건, 브랜드 스토리, 컬러 팔레트를 한 번에 생성한다.
    """

    industry = brief_data.get("industry", "")
    target = brief_data.get("target", "")
    keywords = brief_data.get("keywords", [])
    tone = brief_data.get("tone", "")
    competitors = brief_data.get("competitors", [])
    notes = brief_data.get("notes", "")

    prompt = f"""
너는 전문 브랜드 전략가이자 브랜드 아이덴티티 디자이너야.

아래 브랜드 브리프를 분석하여
실제 상업용 브랜드에 사용할 수 있는 수준의
브랜드 아이덴티티를 기획해줘.

[브랜드 브리프]

업종:
{industry}

타겟 고객:
{target}

핵심 키워드:
{", ".join(keywords)}

톤앤매너:
{tone if tone else "별도 지정 없음"}

경쟁사:
{", ".join(competitors) if competitors else "별도 지정 없음"}

추가 요청사항:
{notes if notes else "별도 요청 없음"}


[기획 요구사항]

1. 브랜드 네이밍 후보 3개를 제안한다.

2. 각 네이밍마다 반드시 다음 정보를 제공한다.
   - 브랜드명
   - 한글로 읽는 법(pronunciation)
   - 이름의 의미 및 유래

3. 네이밍 후보 3개 중 다음 요소를 종합적으로 고려하여
   가장 적합한 브랜드명 1개를 recommended_name으로 추천한다.
   - 브랜드 브리프 적합성
   - 타겟 고객 적합성
   - 발음의 용이성
   - 기억하기 쉬운 정도
   - 차별성
   - 브랜드 확장성

4. 브랜드 톤앤매너에 맞는
   슬로건 또는 태그라인 3개를 제안한다.

5. 슬로건 후보 3개 중
   브랜드 네이밍, 타겟, 톤앤매너,
   브랜드 철학과 가장 잘 어울리는 슬로건 1개를
   recommended_slogan으로 추천한다.

6. 브랜드 스토리는 반드시 한글 기준 250자 이상 350자 이하로 작성한다.
   목표 분량은 약 300자로 한다.
   너무 짧게 요약하지 말고 충분한 내용을 담는다.

7. 브랜드 스토리에는 반드시 다음 3가지 내용을
   구체적이고 자연스럽게 모두 포함한다.
   - 브랜드가 어떤 문제의식과 계기로 시작되었는지 설명하는 탄생 배경
   - 브랜드가 중요하게 생각하는 가치와 원칙을 설명하는 브랜드 철학
   - 앞으로 고객과 사회에 어떤 가치를 제공하고자 하는지 설명하는 미래 비전

   탄생 배경, 브랜드 철학, 미래 비전 중 하나라도 생략하지 않는다.

8. 브랜드에 어울리는 컬러 팔레트를 제안한다.
   - 메인 컬러 1개
   - 서브 컬러 2~3개

9. 컬러는 반드시 HEX 코드로 작성한다.


[네이밍 기준]

- 브랜드명 후보는 정확히 3개를 제안한다.
- 브랜드명을 영문으로 제한하지 않는다.
- 한글, 영문, 한글+영문 조합 모두 가능하다.
- 브랜드 브리프와 타겟 고객을 분석하여
  가장 적합한 언어와 형태를 선택한다.
- 한국 소비자가 쉽게 읽고 기억하고
  말할 수 있는 이름을 우선한다.
- 입으로 발음했을 때 자연스럽고
  기억에 남는 이름을 제안한다.
- 지나치게 길거나 발음하기 어려운 이름은 피한다.
- 업종과 브랜드 철학을 반영한다.
- 너무 흔하거나 평범한 표현은 피한다.
- 경쟁사가 있을 경우 지나치게 유사한 이름은 피한다.
- 각 브랜드명에는 반드시 한글로 읽는 법을 제공한다.
- 영문 브랜드명은 자연스러운 한글 발음을
  pronunciation에 작성한다.
- 한글 브랜드명은 pronunciation에
  해당 브랜드명을 그대로 작성한다.
- 각 이름의 의미와 네이밍 의도를 구체적으로 설명한다.


[차별화 기준]

경쟁사 정보가 있다면
경쟁사의 일반적인 이미지와 차별화될 수 있도록
네이밍, 슬로건, 브랜드 스토리에 반영한다.

추가 요청사항(notes)이 있다면
반드시 브랜드 기획 결과에 반영한다.


[출력 규칙]

반드시 JSON 객체 하나만 반환한다.

JSON에는 다음 항목이 반드시 존재해야 한다.

namings:
브랜드 네이밍 후보 3개를 배열로 작성한다.

각 네이밍 객체에는 다음 필드를 포함한다.

- name
- pronunciation
- meaning

recommended_name:
namings에 제안한 3개의 name 중
가장 적합한 하나를 그대로 작성한다.

slogans:
슬로건 3개를 문자열 배열로 작성한다.

recommended_slogan:
slogans에 제안한 3개의 슬로건 중
가장 적합한 하나를 그대로 작성한다.

story:
한글 기준 250자 이상 350자 이하로 작성한다.
목표 분량은 약 300자로 하며,
탄생 배경, 브랜드 철학, 미래 비전을 반드시 모두 포함한다.

colors:
다음 구조로 작성한다.

main:
메인 컬러 HEX 코드 1개

sub:
서브 컬러 HEX 코드 2~3개


[매우 중요한 검증 규칙]

recommended_name은 반드시
namings에 제안한 3개의 name 중 하나와
문자까지 정확하게 동일해야 한다.

새로운 브랜드명을 추가로 만들지 않는다.

recommended_slogan은 반드시
slogans에 제안한 3개의 슬로건 중 하나와
문자까지 정확하게 동일해야 한다.

새로운 슬로건을 추가로 만들지 않는다.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional brand strategist and "
                        "brand identity designer. "
                        "Return valid JSON only."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={
                "type": "json_object"
            }
        )

        result = json.loads(
            response.choices[0].message.content
        )

        return result

    except Exception as e:
        error_message = str(e).lower()

        if (
            "incorrect api key" in error_message
            or "invalid api key" in error_message
            or "authentication" in error_message
            or "401" in error_message
        ):
            print("🚨 OpenAI API 키 인증에 실패했습니다.")
            print("   .env 파일의 OPENAI_API_KEY가 올바른지 확인해주세요.")
            print("   키를 새로 발급받았다면 저장 후 다시 실행해주세요.")

        else:
            print(f"🚨 브랜드 요소 생성 API 에러: {e}")

        return None


# ============================================================
# 3. 필수 입력값 검증
# ============================================================

def validate_brief(brief_data):
    """
    과제 요구사항의 필수 필드를 검사한다.
    필수 필드:
    industry, target, keywords
    """

    required_fields = [
        "industry",
        "target",
        "keywords"
    ]

    missing_fields = []

    for field in required_fields:
        if field not in brief_data:
            missing_fields.append(field)
            continue

        value = brief_data.get(field)

        if value is None or value == "":
            missing_fields.append(field)

        if field == "keywords":
            if not isinstance(value, list) or len(value) == 0:
                missing_fields.append(field)

    if missing_fields:
        print("\n🚨 브리프 필수 입력값이 누락되었습니다.")
        print(
            "   누락 필드:",
            ", ".join(sorted(set(missing_fields)))
        )
        print(
            "   필수 필드: industry, target, keywords"
        )
        return False

    return True


# ============================================================
# 4. 생성 결과 검증
# ============================================================

def validate_brand_result(result):
    """
    LLM이 과제 요구사항에 맞는 구조를 반환했는지 검사한다.
    """

    try:
        namings = result["namings"]
        slogans = result["slogans"]
        story = result["story"]
        colors = result["colors"]

        if len(namings) < 3:
            raise ValueError(
                "네이밍 후보가 3개 미만입니다."
            )

        if len(slogans) < 3:
            raise ValueError(
                "슬로건이 3개 미만입니다."
            )

        if not story:
            raise ValueError(
                "브랜드 스토리가 없습니다."
            )

        if "main" not in colors:
            raise ValueError(
                "메인 컬러가 없습니다."
            )

        if "sub" not in colors:
            raise ValueError(
                "서브 컬러가 없습니다."
            )

        if len(colors["sub"]) < 2:
            raise ValueError(
                "서브 컬러가 2개 미만입니다."
            )

        return True

    except Exception as e:
        print(
            f"🚨 AI 생성 결과 검증 실패: {e}"
        )
        return False


# ============================================================
# 5. 컬러 팔레트 이미지 생성
# ============================================================

def save_color_palette(colors, output_folder):
    """
    브랜드 컬러를 matplotlib으로 시각화하여 PNG로 저장한다.
    """

    print("[4/5] 컬러 팔레트 생성 중...")

    try:
        main_color = colors["main"]
        sub_colors = colors["sub"]

        all_colors = [
            main_color
        ] + sub_colors

        fig, ax = plt.subplots(
            figsize=(8, 2.5)
        )

        for i, color in enumerate(all_colors):
            ax.add_patch(
                plt.Rectangle(
                    (i, 0),
                    1,
                    1,
                    color=color
                )
            )

        ax.set_xlim(
            0,
            len(all_colors)
        )

        ax.set_ylim(
            0,
            1
        )

        ax.axis("off")

        palette_path = os.path.join(
            output_folder,
            "color_palette.png"
        )

        plt.savefig(
            palette_path,
            bbox_inches="tight",
            dpi=200
        )

        plt.close()

        print(
            f"  - 메인: {main_color}"
        )

        print(
            f"  - 서브: {', '.join(sub_colors)}"
        )

        print(
            f"  - 저장: {palette_path}"
        )

        return True

    except Exception as e:
        print(
            f"🚨 컬러 팔레트 생성 에러: {e}"
        )
        return False


# ============================================================
# 6. AI 로고 생성
# ============================================================

def generate_logos(
    brand_name,
    slogan,
    story,
    industry,
    keywords,
    tone,
    colors,
    competitors,
    notes,
    output_folder
):
    """
    GPT Image API를 사용하여
    서로 다른 방향의 로고 시안 2개를 생성한다.
    """

    print("[5/5] 로고 시안 생성 중...")

    main_color = colors.get(
        "main",
        "#000000"
    )

    sub_colors = colors.get(
        "sub",
        []
    )

    competitor_text = (
        ", ".join(competitors)
        if competitors
        else "None"
    )

    notes_text = (
        notes
        if notes
        else "None"
    )

    logo_styles = [
        """
DESIGN DIRECTION A

Create a sophisticated abstract brand symbol.

Use:
- clean geometric forms
- balanced negative space
- memorable silhouette
- refined visual proportions

The concept should feel like
a premium branding agency design.

Avoid obvious stock-style visual clichés.
""",

        """
DESIGN DIRECTION B

Create a distinctive modern emblem
with a refined and organic visual language.

Use:
- simple but original geometry
- elegant visual rhythm
- strong visual balance
- memorable icon structure

The symbol should remain recognizable
even when displayed at a very small size.

Avoid generic AI-generated logo aesthetics.
"""
    ]

    success_count = 0

    for i, logo_style in enumerate(
        logo_styles,
        start=1
    ):

        try:
            image_prompt = f"""
Create a premium professional logo symbol
for the brand '{brand_name}'.

BRAND INFORMATION

Brand name:
{brand_name}

Recommended slogan:
{slogan}

Brand story:
{story}

Industry:
{industry}

Brand keywords:
{", ".join(keywords)}

Brand tone:
{tone if tone else "Not specified"}

Competitors:
{competitor_text}

Additional request:
{notes_text}


BRAND COLOR PALETTE

Primary color:
{main_color}

Secondary colors:
{", ".join(sub_colors)}

Use the supplied brand colors
as the main visual palette.


DESIGN DIRECTION

{logo_style}


DESIGN QUALITY

The logo must be:

- premium
- modern
- minimal
- sophisticated
- distinctive
- timeless
- professional
- visually balanced
- commercially usable

The logo should be suitable for:

- product packaging
- website
- mobile application
- social media
- business cards
- signage
- print materials


IMPORTANT DESIGN RULES

Avoid generic AI logo designs.

Do not automatically use:

- generic leaves
- recycling symbols
- globes
- water drops
- random circles
- stock eco icons
- clip-art style graphics

unless they are genuinely necessary
for the brand concept.

If competitors are provided,
avoid creating a symbol that looks
too visually similar to them.


TECHNICAL STYLE

- clean vector-style artwork
- flat design
- precise geometry
- strong silhouette
- clean edges
- balanced negative space
- no mockup
- no photograph
- no 3D rendering
- no shadow
- no unnecessary effects
- no gradient
- plain white background


VERY IMPORTANT

Generate the SYMBOL ONLY.

Do NOT include:

- brand name
- Korean characters
- English letters
- slogan
- typography
- random text
- fake writing

The final image must contain
one professional logo symbol
centered on a clean white background.
"""

            response = client.images.generate(
                model="gpt-image-1",
                prompt=image_prompt,
                size="1024x1024",
                quality="medium"
            )

            image_base64 = (
                response.data[0].b64_json
            )

            image_bytes = base64.b64decode(
                image_base64
            )

            image_path = os.path.join(
                output_folder,
                f"logo_0{i}.png"
            )

            with open(
                image_path,
                "wb"
            ) as f:
                f.write(
                    image_bytes
                )

            print(
                f"  - 저장: {image_path}"
            )

            success_count += 1

        except Exception as e:
            print(
                f"🚨 로고 시안 {i} 생성 에러: {e}"
            )
            print(
                "   다음 로고 시안 생성을 계속 진행합니다."
            )

    return success_count


# ============================================================
# 7. CLI 결과 출력
# ============================================================

def print_brand_result(brand_result):
    """
    브랜드 네이밍, 슬로건, 스토리를
    터미널에 단계별로 표시한다.
    """

    # ----------------------------------------------------
    # 1. 브랜드 네이밍
    # ----------------------------------------------------

    print("\n[1/5] 브랜드 네이밍 제안")

    recommended_name = brand_result.get(
        "recommended_name",
        ""
    )

    for i, item in enumerate(
        brand_result["namings"][:3],
        start=1
    ):
        name = item["name"]
        pronunciation = item.get(
            "pronunciation",
            name
        )
        meaning = item["meaning"]

        if name == recommended_name:
            recommendation = " ⭐ AI 추천"
        else:
            recommendation = ""

        print(
            f"\n  {i}. {name} ({pronunciation})"
            f"{recommendation}"
        )

        print(
            f"     - {meaning}"
        )

    # ----------------------------------------------------
    # 2. 슬로건
    # ----------------------------------------------------

    print("\n[2/5] 슬로건 제안")

    recommended_slogan = brand_result.get(
        "recommended_slogan",
        ""
    )

    for i, slogan in enumerate(
        brand_result["slogans"][:3],
        start=1
    ):
        if slogan == recommended_slogan:
            recommendation = " ⭐ AI 추천"
        else:
            recommendation = ""

        print(
            f'  {i}. "{slogan}"{recommendation}'
        )

    # ----------------------------------------------------
    # 3. 브랜드 스토리
    # ----------------------------------------------------

    print("\n[3/5] 브랜드 스토리 생성 완료")

    story = brand_result["story"]

    print(
        f"  - 스토리 생성 완료 ({len(story)}자)"
    )

    print(
        f"  - {story}"
    )


# ============================================================
# 8. 메인 프로그램
# ============================================================

def main():

    print(
        "\n🎨 AI 브랜드 아이덴티티 생성기\n"
    )

    brief_path = input(
        "브리프 파일 경로를 입력하세요 "
        "(예: brief.json): "
    )

    output_folder = input(
        "출력 폴더 경로를 입력하세요 "
        "(엔터 시 ./output): "
    )

    if output_folder.strip() == "":
        output_folder = "./output"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    try:
        # ----------------------------------------------------
        # 브리프 JSON 파일 읽기
        # ----------------------------------------------------

        with open(
            brief_path,
            "r",
            encoding="utf-8"
        ) as file:
            brief_data = json.load(file)

        print(
            "\n✅ 주문서(브리프) 확인 완료!\n"
        )

        # ----------------------------------------------------
        # 필수 필드 검사
        # ----------------------------------------------------

        if not validate_brief(brief_data):
            return

        # ----------------------------------------------------
        # 브랜드 요소 AI 생성
        # ----------------------------------------------------

        brand_result = generate_brand_identity(
            brief_data
        )

        if not brand_result:
            print(
                "\n🚨 브랜드 요소 생성에 실패했습니다."
            )
            return

        # ----------------------------------------------------
        # AI 생성 결과 구조 검사
        # ----------------------------------------------------

        if not validate_brand_result(
            brand_result
        ):
            print(
                "\n🚨 AI 결과 형식이 "
                "과제 요구사항과 맞지 않습니다."
            )
            return

        # ----------------------------------------------------
        # 텍스트 결과 저장
        # ----------------------------------------------------

        result_path = os.path.join(
            output_folder,
            "brand_result.json"
        )

        with open(
            result_path,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                brand_result,
                f,
                ensure_ascii=False,
                indent=4
            )

        # ----------------------------------------------------
        # 터미널에 단계별 결과 출력
        # ----------------------------------------------------

        print_brand_result(
            brand_result
        )

        # ----------------------------------------------------
        # 추천 브랜드명 / 슬로건 추출
        # ----------------------------------------------------

        recommended_name = brand_result.get(
            "recommended_name",
            brand_result["namings"][0]["name"]
        )

        recommended_slogan = brand_result.get(
            "recommended_slogan",
            brand_result["slogans"][0]
        )

        story = brand_result["story"]

        # ----------------------------------------------------
        # 브리프 정보 추출
        # ----------------------------------------------------

        industry = brief_data.get(
            "industry",
            ""
        )

        keywords = brief_data.get(
            "keywords",
            []
        )

        tone = brief_data.get(
            "tone",
            ""
        )

        competitors = brief_data.get(
            "competitors",
            []
        )

        notes = brief_data.get(
            "notes",
            ""
        )

        colors = brand_result["colors"]

        # ----------------------------------------------------
        # 컬러 팔레트 생성
        # ----------------------------------------------------

        save_color_palette(
            colors,
            output_folder
        )

        # ----------------------------------------------------
        # 로고 시안 생성
        # ----------------------------------------------------

        logo_count = generate_logos(
            recommended_name,
            recommended_slogan,
            story,
            industry,
            keywords,
            tone,
            colors,
            competitors,
            notes,
            output_folder
        )

        # ----------------------------------------------------
        # 최종 완료 메시지
        # ----------------------------------------------------

        print(
            "\n========================================"
        )
        print(
            "✅ 브랜드 아이덴티티 생성 완료!"
        )
        print(
            "========================================"
        )

        print(
            f"\nAI 추천 브랜드명: {recommended_name}"
        )

        print(
            f"AI 추천 슬로건: {recommended_slogan}"
        )

        print(
            f"출력 폴더: {output_folder}"
        )

        print(
            "\n생성 결과물:"
        )

        print(
            "  - brand_result.json"
        )

        print(
            "  - color_palette.png"
        )

        for i in range(
            1,
            logo_count + 1
        ):
            print(
                f"  - logo_{i:02d}.png"
            )

    except FileNotFoundError:

        print(
            f"\n🚨 에러: "
            f"'{brief_path}' 파일을 찾을 수 없습니다."
        )

    except json.JSONDecodeError:

        print(
            "\n🚨 에러: brief.json의 "
            "JSON 형식이 올바르지 않습니다."
        )

    except PermissionError:

        print(
            "\n🚨 에러: 파일 또는 폴더에 "
            "접근할 권한이 없습니다."
        )

    except Exception as e:

        print(
            f"\n🚨 프로그램 실행 중 "
            f"예상하지 못한 에러 발생: {e}"
        )


# ============================================================
# 프로그램 시작
# ============================================================

if __name__ == "__main__":
    main()