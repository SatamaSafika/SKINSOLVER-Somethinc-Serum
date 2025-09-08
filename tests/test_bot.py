import pytest
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bot import get_response, detect_goal, detect_focus, detect_type

# ================================
# Unit test untuk deteksi
# ================================
@pytest.mark.parametrize("msg,expected_goal", [
    ("Aku mau kulit lebih cerah", "bright"),
    ("lagi jerawat parah", "acne"),
    ("supaya ga cepat keriput", "antiaging"),
])
def test_detect_goal(msg, expected_goal):
    assert detect_goal(msg) == expected_goal


@pytest.mark.parametrize("msg,expected_focus", [
    ("kulitku kusam banget", "kusam"),
    ("ada bekas jerawat susah hilang", "bekas"),
    ("muncul flek hitam hyperpigmentasi", "hyper"),
])
def test_detect_focus(msg, expected_focus):
    assert detect_focus(msg) == expected_focus


@pytest.mark.parametrize("msg,expected_type", [
    ("kulitku sensitif", "sensitive"),
    ("aku normal skin", "normal"),
    ("kulitku gampang berminyak", "oily"),
])
def test_detect_type(msg, expected_type):
    assert detect_type(msg) == expected_type


# ================================
# Integration test untuk flow
# ================================
def test_full_flow_bright_kusam_sensitive():
    """Simulasi: user → bright → kusam → sensitive"""
    uid = 123

    # Greeting
    from bot import handle_greeting
    resp1 = handle_greeting(uid)

    # Goal
    resp2 = get_response(uid, "mau kulit cerah")
    assert "goal kamu mencerahkan" in resp2.lower()

    # Focus
    resp3 = get_response(uid, "kulitku kusam")
    assert "tipe kulitmu" in resp3.lower()

    # Type
    resp4 = get_response(uid, "kulitku sensitif")
    assert "sensitif" in resp4.lower() or "niacinamide" in resp4.lower()


def test_full_flow_acne_jerawat():
    """Simulasi: user → acne → jerawat"""
    uid = 456

    get_response(uid, "halo")  # greeting
    get_response(uid, "lagi jerawat parah")  # goal
    resp = get_response(uid, "jerawat aktif banget")  # focus

    assert "jerawat" in resp.lower() or "salicylic" in resp.lower()


def test_full_flow_antiaging_normal():
    """Simulasi: user → antiaging → normal skin"""
    uid = 789

    get_response(uid, "hi")  # greeting
    get_response(uid, "aku mau anti aging")  # goal
    resp = get_response(uid, "kulitku normal")  # type

    assert "retinol" in resp.lower() or "moisturizer" in resp.lower()
