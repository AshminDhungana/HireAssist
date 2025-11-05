from app.api.v1.matching import (
    calculate_skill_match,
    calculate_experience_score,
    calculate_education_score,
    calculate_overall_score,
)


def test_calculate_skill_match_basic():
    req = "Looking for Python and React with Docker experience"
    skills = ["Python", "Java", "React", "AWS", "Docker"]
    score = calculate_skill_match(req, skills)
    # 3 of 5 skills match by substring -> 0.6
    assert 0.59 <= score <= 0.61


def test_experience_score_tiers():
    senior_req = "Senior backend engineer"
    junior_req = "Junior developer"
    mid_req = "Software engineer"

    assert calculate_experience_score(senior_req, 5) >= calculate_experience_score(senior_req, 3)
    assert calculate_experience_score(junior_req, 1) >= calculate_experience_score(junior_req, 4)
    assert calculate_experience_score(mid_req, 3) >= calculate_experience_score(mid_req, 1)


def test_education_score_levels():
    assert calculate_education_score("PhD in CS") == 1.0
    assert calculate_education_score("Master of Science") == 0.9
    assert calculate_education_score("Bachelor of Arts") == 0.8
    assert calculate_education_score("Associate Degree") == 0.7
    assert calculate_education_score(None) == 0.5


def test_overall_score_weighting():
    # skills 0.8, experience 0.6, education 0.9
    overall = calculate_overall_score(0.8, 0.6, 0.9)
    # 0.8*0.5 + 0.6*0.3 + 0.9*0.2 = 0.4 + 0.18 + 0.18 = 0.76
    assert 0.75 <= overall <= 0.77


