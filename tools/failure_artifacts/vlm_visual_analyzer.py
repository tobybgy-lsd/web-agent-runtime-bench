# -*- coding: utf-8 -*-
"""
VLM 视觉诊断扩展模块
VLM Visual Analyzer - 图像层面的视觉失败分析

能力:
- 基础图像分析 (无需VLM API): 颜色分布、亮度、遮挡率估算
- VLM接口层: 标准化的截图+问题描述，可接入 GPT-4V/Claude Vision/Gemini Vision
- 与 visual_failure_doctor.py 联动: 补充图像层面的证据
- 本地模拟 VLM 响应 (用于测试)
"""
from __future__ import annotations

import base64
import json
import struct
import zlib
from pathlib import Path
from typing import Any


# ─────────────────────────────────────────────────────────────────────────
# 基础图像分析 (纯Python，无需Pillow/OpenCV)
# ─────────────────────────────────────────────────────────────────────────

def analyze_png_basic(png_path: str | Path) -> dict[str, Any]:
    """
    纯 Python 解析 PNG 图像基础属性 (无需第三方库)
    Returns: width, height, bit_depth, color_type, has_alpha, estimated_dark_ratio
    """
    path = Path(png_path)
    if not path.exists():
        return {"error": "file not found", "path": str(png_path)}

    data = path.read_bytes()
    result: dict[str, Any] = {"path": str(path), "size_bytes": len(data)}

    # PNG header signature check
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        return {**result, "error": "not a valid PNG file"}

    # Parse IHDR chunk (bytes 8-33)
    try:
        width  = struct.unpack(">I", data[16:20])[0]
        height = struct.unpack(">I", data[20:24])[0]
        bit_depth  = data[24]
        color_type = data[25]  # 0=gray,2=RGB,3=indexed,4=gray+alpha,6=RGBA
        result.update({
            "width": width,
            "height": height,
            "bit_depth": bit_depth,
            "color_type": color_type,
            "has_alpha": color_type in (4, 6),
            "pixel_count": width * height,
        })
    except (struct.error, IndexError):
        result["error"] = "could not parse IHDR"
        return result

    # Estimate image entropy from compressed size vs uncompressed
    # Low ratio = low entropy = possibly blank/solid (loading screen, dark overlay)
    raw_size = width * height * (4 if color_type == 6 else 3)
    compressed_size = len(data)
    if raw_size > 0:
        compression_ratio = compressed_size / raw_size
        # Very low ratio = blank/uniform image (possible overlay or not-loaded)
        result["compression_ratio"] = round(compression_ratio, 4)
        result["estimated_blank"] = compression_ratio < 0.05
        result["estimated_uniform_color"] = compression_ratio < 0.10

    return result


def extract_dominant_color_hint(png_path: str | Path) -> dict[str, Any]:
    """
    从 PNG IDAT chunk 采样估算主色调 (简化版)
    用于检测: 深色蒙层(overlay)、全白(未加载)、正常页面
    """
    path = Path(png_path)
    if not path.exists():
        return {"error": "file not found"}

    data = path.read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        return {"error": "not PNG"}

    # 收集所有 IDAT chunks 并解压
    idat_data = bytearray()
    pos = 8
    try:
        while pos + 12 <= len(data):
            chunk_len  = struct.unpack(">I", data[pos:pos+4])[0]
            chunk_type = data[pos+4:pos+8]
            chunk_data = data[pos+8:pos+8+chunk_len]
            if chunk_type == b'IDAT':
                idat_data.extend(chunk_data)
            pos += 12 + chunk_len
    except Exception:
        return {"error": "chunk parse error"}

    if not idat_data:
        return {"error": "no IDAT data"}

    try:
        raw = zlib.decompress(bytes(idat_data))
    except zlib.error:
        return {"error": "decompression failed"}

    # Sample first few scan lines
    color_type = data[25]
    width = struct.unpack(">I", data[16:20])[0]
    channels = {0:1, 2:3, 3:1, 4:2, 6:4}.get(color_type, 3)
    stride = 1 + width * channels  # filter byte + pixels

    samples = []
    for row in range(min(10, len(raw) // stride)):
        line_start = row * stride + 1  # skip filter byte
        for col in range(0, min(10, width)) :
            px_start = line_start + col * channels
            if px_start + channels <= len(raw):
                px = raw[px_start:px_start+channels]
                if channels >= 3:
                    samples.append((px[0], px[1], px[2]))
                elif channels == 1:
                    samples.append((px[0], px[0], px[0]))

    if not samples:
        return {"error": "no samples extracted"}

    avg_r = sum(s[0] for s in samples) / len(samples)
    avg_g = sum(s[1] for s in samples) / len(samples)
    avg_b = sum(s[2] for s in samples) / len(samples)
    brightness = (avg_r + avg_g + avg_b) / 3

    # 颜色语义判断 (精确阈值)
    # 判断是否是灰色调: R≈G≈B (色彩方差低)
    rgb_variance = ((avg_r - brightness)**2 + (avg_g - brightness)**2 + (avg_b - brightness)**2) / 3
    is_grayish = rgb_variance < 400  # 标准差 < 20 认为接近灰色

    if brightness < 30:
        color_hint = "very_dark"
        interpretation = "可能是深色蒙层(overlay)或截图全黑(未加载)"
    elif brightness > 230:
        color_hint = "very_bright"
        interpretation = "可能是空白页面或页面未加载完成"
    elif 110 < brightness <= 220 and is_grayish:
        # 灰色调 + 中等亮度 → skeleton/loading 占位符
        color_hint = "neutral_gray"
        interpretation = "可能是 skeleton/loading 占位符"
    else:
        color_hint = "normal"
        interpretation = "亮度正常，页面可能已加载"

    return {
        "sample_count": len(samples),
        "avg_brightness": round(brightness, 1),
        "avg_rgb": (round(avg_r,1), round(avg_g,1), round(avg_b,1)),
        "color_hint": color_hint,
        "interpretation": interpretation,
    }


# ─────────────────────────────────────────────────────────────────────────
# VLM 接口层 (标准化问题包，可接入真实API)
# ─────────────────────────────────────────────────────────────────────────

VISUAL_ANALYSIS_PROMPTS = {
    "general_failure": """
You are diagnosing a browser automation visual failure from a sanitized screenshot.
Choose the best matching type:
1. overlay_blocked: a modal, overlay, or dialog covers the target element
2. screenshot_not_loaded: the page is not fully loaded; skeleton/spinner is visible
3. coordinate_drift: click target appears shifted or outside the expected position
4. dom_not_visible: target element is not visible in the screenshot
5. no_failure: the page appears normal

Return JSON: {"primary_type": "<type>", "confidence": <0.0-1.0>, "reasoning": "<reason>"}
""",
    "overlay_check": """
Does this screenshot show a modal, overlay, or mask covering page content?
If yes, describe its color and approximate coverage (0-100%).
Return JSON: {"has_overlay": true/false, "coverage_percent": <0-100>, "overlay_color": "<description>"}
""",
    "loading_check": """
Does this screenshot appear fully loaded?
Check for spinners, skeleton placeholders, loading text, and blank regions.
Return JSON: {"fully_loaded": true/false, "loading_indicators": ["<indicator>", ...]}
""",
}


def build_vlm_request(
    screenshot_path: str | Path,
    prompt_key: str = "general_failure",
    custom_prompt: str | None = None,
    extra_context: dict | None = None
) -> dict[str, Any]:
    """
    构建标准化的 VLM 请求包。
    可直接发送给 OpenAI GPT-4V / Anthropic Claude Vision / Google Gemini Vision API。
    
    Returns: {
        "provider_agnostic": {...},  # 通用格式
        "openai_format": {...},      # OpenAI API格式
        "anthropic_format": {...},   # Claude API格式
    }
    """
    path = Path(screenshot_path)
    prompt = custom_prompt or VISUAL_ANALYSIS_PROMPTS.get(prompt_key, VISUAL_ANALYSIS_PROMPTS["general_failure"])
    
    if extra_context:
        prompt += f"\n\nAdditional context: {json.dumps(extra_context, ensure_ascii=False)}"

    # Base64 encode the image
    if path.exists() and path.stat().st_size > 0:
        img_bytes = path.read_bytes()
        # Check if it's a real PNG or a raw byte stub
        is_real_png = img_bytes[:8] == b'\x89PNG\r\n\x1a\n'
        is_stub = not is_real_png or len(img_bytes) < 50
        if not is_stub:
            img_b64 = base64.b64encode(img_bytes).decode()
            media_type = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
        else:
            img_b64 = None
    else:
        img_b64 = None
        is_stub = True

    request_pack = {
        "provider_agnostic": {
            "prompt": prompt.strip(),
            "image_path": str(path),
            "image_b64": img_b64,
            "is_stub_image": is_stub,
            "prompt_key": prompt_key,
        },
        "openai_format": {
            "model": "gpt-4o",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt.strip()},
                    *([{
                        "type": "image_url",
                        "image_url": {"url": f"data:{media_type};base64,{img_b64}"}
                    }] if img_b64 else [{"type": "text", "text": "[IMAGE STUB - not a real screenshot]"}])
                ]
            }],
            "max_tokens": 300,
        },
        "anthropic_format": {
            "model": "claude-opus-4-5",
            "max_tokens": 300,
            "messages": [{
                "role": "user",
                "content": [
                    *([{
                        "type": "image",
                        "source": {"type": "base64", "media_type": "image/png", "data": img_b64}
                    }] if img_b64 else []),
                    {"type": "text", "text": prompt.strip()}
                ]
            }]
        }
    }

    return request_pack


def call_vlm_api(request_pack: dict, provider: str = "mock") -> dict[str, Any]:
    """
    调用 VLM API 获取视觉分析结果。
    provider: "openai" | "anthropic" | "mock"
    
    mock 模式: 基于图像基础分析模拟VLM响应 (用于测试/无API密钥时)
    """
    if provider == "mock":
        return _mock_vlm_response(request_pack)

    elif provider == "openai":
        try:
            import openai
            client = openai.OpenAI()
            resp = client.chat.completions.create(**request_pack["openai_format"])
            content = resp.choices[0].message.content
            return {"raw_response": content, "parsed": _try_parse_json(content), "provider": "openai"}
        except ImportError:
            return {"error": "openai package not installed", "hint": "pip install openai"}
        except Exception as e:
            return {"error": str(e), "provider": "openai"}

    elif provider == "anthropic":
        try:
            import anthropic
            client = anthropic.Anthropic()
            resp = client.messages.create(**request_pack["anthropic_format"])
            content = resp.content[0].text
            return {"raw_response": content, "parsed": _try_parse_json(content), "provider": "anthropic"}
        except ImportError:
            return {"error": "anthropic package not installed", "hint": "pip install anthropic"}
        except Exception as e:
            return {"error": str(e), "provider": "anthropic"}

    return {"error": f"unknown provider: {provider}"}


def _mock_vlm_response(request_pack: dict) -> dict[str, Any]:
    """基于图像基础分析模拟VLM响应"""
    image_path = request_pack["provider_agnostic"].get("image_path", "")
    prompt_key = request_pack["provider_agnostic"].get("prompt_key", "general_failure")
    
    # 尝试基础图像分析
    basic = analyze_png_basic(image_path)
    color = extract_dominant_color_hint(image_path) if Path(image_path).exists() else {}

    hint = color.get("color_hint", "normal")
    brightness = color.get("avg_brightness", 128)
    is_stub = request_pack["provider_agnostic"].get("is_stub_image", True)

    if is_stub:
        parsed = {
            "primary_type": "unknown",
            "confidence": 0.30,
            "reasoning": "[MOCK] Image is a stub. Cannot perform visual analysis.",
            "note": "Use provider='openai' or 'anthropic' for real VLM analysis"
        }
    elif hint == "very_dark":
        parsed = {
            "primary_type": "overlay_blocked",
            "confidence": 0.78,
            "reasoning": f"[MOCK] Very dark image (brightness={brightness:.0f}/255). Likely a dark overlay/modal."
        }
    elif hint == "very_bright":
        parsed = {
            "primary_type": "screenshot_not_loaded",
            "confidence": 0.72,
            "reasoning": f"[MOCK] Very bright/blank image (brightness={brightness:.0f}/255). Page may not have loaded."
        }
    elif hint == "neutral_gray":
        parsed = {
            "primary_type": "screenshot_not_loaded",
            "confidence": 0.65,
            "reasoning": f"[MOCK] Gray uniform tones (brightness={brightness:.0f}/255). Possible skeleton/loading state."
        }
    else:
        # hint == "normal": colorful or normal-brightness image
        parsed = {
            "primary_type": "no_failure",
            "confidence": 0.60,
            "reasoning": f"[MOCK] Image appears normally lit (brightness={brightness:.0f}/255). No obvious visual failure."
        }

    return {
        "provider": "mock",
        "parsed": parsed,
        "image_analysis": {**basic, **color},
        "note": "This is a MOCK VLM response based on basic image analysis. For real VLM: call_vlm_api(pack, provider='openai')"
    }


def _try_parse_json(text: str) -> dict:
    """尝试从VLM文本响应中提取JSON"""
    import re
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Try extracting JSON block
    m = re.search(r'\{[^{}]+\}', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            pass
    return {"raw_text": text}


# ─────────────────────────────────────────────────────────────────────────
# 与 visual_failure_doctor 联动
# ─────────────────────────────────────────────────────────────────────────

def enhance_diagnosis_with_vlm(
    basic_diagnosis: dict[str, Any],
    artifact_dir: str | Path,
    provider: str = "mock"
) -> dict[str, Any]:
    """
    在 visual_failure_doctor 的基础诊断结果上，叠加 VLM 图像层面分析。
    
    Args:
        basic_diagnosis: diagnose_visual_failure() 的返回结果
        artifact_dir: 证据目录
        provider: "mock" | "openai" | "anthropic"
    
    Returns: 增强后的诊断结果 (含 vlm_analysis 字段)
    """
    path = Path(artifact_dir)
    screenshot = path / "screenshot.png"

    if not screenshot.exists():
        enhanced = dict(basic_diagnosis)
        enhanced["vlm_analysis"] = {"skipped": True, "reason": "no screenshot.png found"}
        return enhanced

    # 构建VLM请求 (注入DOM上下文)
    extra_ctx = {}
    if (path / "dom_snapshot.html").exists():
        dom_excerpt = (path / "dom_snapshot.html").read_text(encoding="utf-8", errors="ignore")[:500]
        extra_ctx["dom_excerpt"] = dom_excerpt
    if (path / "click_coordinates.json").exists():
        try:
            coords = json.loads((path / "click_coordinates.json").read_text(encoding="utf-8"))
            extra_ctx["click_coords"] = coords
        except Exception:
            pass

    vlm_pack = build_vlm_request(screenshot, prompt_key="general_failure", extra_context=extra_ctx)
    vlm_result = call_vlm_api(vlm_pack, provider=provider)

    # 合并诊断结果
    enhanced = dict(basic_diagnosis)
    enhanced["vlm_analysis"] = vlm_result

    # 如果VLM给出了更高置信度的结果，更新主诊断
    vlm_parsed = vlm_result.get("parsed", {})
    vlm_type = vlm_parsed.get("primary_type", "")
    vlm_conf = float(vlm_parsed.get("confidence", 0.0))
    current_conf = basic_diagnosis.get("confidence", 0.0)

    KNOWN_TYPES = {"overlay_blocked", "screenshot_not_loaded", "coordinate_drift",
                   "dom_not_visible", "ocr_mismatch", "viewport_scale_drift",
                   "screenshot_dom_inconsistency"}

    if vlm_type in KNOWN_TYPES and vlm_conf > current_conf + 0.1:
        enhanced["vlm_upgraded_diagnosis"] = True
        enhanced["original_primary_type"] = basic_diagnosis.get("primary_failure_type")
        enhanced["primary_failure_type"] = vlm_type
        enhanced["confidence"] = max(current_conf, vlm_conf)
        enhanced["confidence_label"] = f"{enhanced['confidence']:.0%}"
        enhanced["findings"].append(
            f"VLM upgraded diagnosis: {vlm_type} (confidence {vlm_conf:.0%}) - {vlm_parsed.get('reasoning', '')[:100]}"
        )
    else:
        enhanced["vlm_upgraded_diagnosis"] = False
        if vlm_type and vlm_type != "unknown":
            enhanced["findings"].append(
                f"VLM image analysis: {vlm_type} (confidence {vlm_conf:.0%}) - {vlm_parsed.get('reasoning', '')[:100]}"
            )

    return enhanced
