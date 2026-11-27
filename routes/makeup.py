# routes/makeup.py
from flask import Blueprint, render_template, request
from services import makeup_service

makeup_bp = Blueprint("makeup", __name__, url_prefix="/makeup")


@makeup_bp.route('/')
def makeup_index():
    # 表单选项（肤质、肤色、场景）
    skin_type = request.args.get("skin_type", "中性")
    skin_tone = request.args.get("skin_tone", "自然偏白")
    scene = request.args.get("scene", "auto")

    weather = makeup_service.get_nanjing_weather()
    advice = makeup_service.recommend_makeup(
        weather, skin_type=skin_type, skin_tone=skin_tone, scene=scene
    )
    return render_template(
        "makeup.html",
        weather=weather,
        advice=advice,
        skin_types=makeup_service.SKIN_TYPES,
        skin_tones=makeup_service.SKIN_TONES,
        skin_type=skin_type,
        skin_tone=skin_tone,
        scene=scene,
    )
