import pytest
from app.services.detection_service import score_email


def test_known_ats_domain_scores_high():
    result = score_email(
        sender_email="no-reply@greenhouse.io",
        subject="Your application to Acme Corp",
        body_snippet="Thank you for applying to the Software Engineer role.",
    )
    assert result.score >= 50
    assert result.is_job is True


def test_no_reply_alone_does_not_classify():
    result = score_email(
        sender_email="no-reply@newsletter.com",
        subject="Weekly digest",
        body_snippet="Here are this week's top stories.",
    )
    assert result.is_job is False


def test_job_keywords_in_subject_boost_score():
    result = score_email(
        sender_email="careers@somecompany.com",
        subject="Thank you for applying to Software Engineer",
        body_snippet="",
    )
    assert result.score >= 50
    assert result.is_job is True


def test_rejection_email_infers_status():
    result = score_email(
        sender_email="no-reply@greenhouse.io",
        subject="Update on your application",
        body_snippet="Unfortunately, we will not be moving forward with your application.",
    )
    assert result.inferred_status == "rejected"


def test_offer_email_infers_status():
    result = score_email(
        sender_email="recruiting@company.com",
        subject="Offer letter from Acme",
        body_snippet="We are pleased to extend an offer letter for the role.",
    )
    assert result.inferred_status == "offer"


def test_thread_bonus_pushes_borderline_over_threshold():
    # Low-signal email that would normally not classify
    result_without = score_email(
        sender_email="no-reply@somecompany.com",
        subject="Following up",
        body_snippet="",
        existing_thread_classified=False,
    )
    result_with = score_email(
        sender_email="no-reply@somecompany.com",
        subject="Following up",
        body_snippet="",
        existing_thread_classified=True,
    )
    assert result_with.score > result_without.score
