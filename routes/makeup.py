# routes/makeup.py
from flask import Blueprint, render_template, request
from services import makeup_service

makeup_bp = Blueprint("makeup", __name__, url_prefix="/makeup")


@makeup_bp.route('/')
def makeup_index():
    # 表单选项（肤质、肤色、妆容场景、穿搭场景）
    skin_type = request.args.get("skin_type", "中性")
    skin_tone = request.args.get("skin_tone", "自然偏白")
    scene = request.args.get("scene", "auto")
    outfit_scene = request.args.get("outfit_scene", "日常通勤")
    gender = request.args.get("gender", "女")
    outfit_style = request.args.get("outfit_style", "随性休闲")

    weather = makeup_service.get_nanjing_weather()
    advice = makeup_service.recommend_makeup(
        weather, skin_type=skin_type, skin_tone=skin_tone, scene=scene
    )
    outfit = makeup_service.recommend_outfit(
        weather, scene=outfit_scene, gender=gender, style=outfit_style
    )

    return render_template(
        "makeup.html",
        weather=weather,
        advice=advice,
        outfit=outfit,
        skin_types=makeup_service.SKIN_TYPES,
        skin_tones=makeup_service.SKIN_TONES,
        makeup_scenes=makeup_service.MAKEUP_SCENES,
        outfit_scenes=makeup_service.OUTFIT_SCENES,
        outfit_styles=makeup_service.OUTFIT_STYLES,
        genders=makeup_service.GENDERS,
        skin_type=skin_type,
        skin_tone=skin_tone,
        scene=scene,
        outfit_scene=outfit_scene,
        outfit_style=outfit_style,
        gender=gender,
    )
