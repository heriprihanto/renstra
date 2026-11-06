import json
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.schemas.ai import SmartRecommendationRequest
from app.services.smart_indicator_ai import (
    _build_user_prompt,
    _generate_smart_fallback,
    generate_smart_recommendations,
)


class IndicatorPromptTests(unittest.TestCase):
    def test_child_measurement_context_is_preserved(self):
        req = SmartRecommendationRequest(
            level="kegiatan", uraian='Layanan "terpadu"',
            subkegiatan_list=[dict(uraisubkegiatan="Pelayanan", kinerja="Tuntas",
                                  indikator_uraian="Jumlah layanan selesai",
                                  satuan="Layanan", target="12")],
        )
        prompt = _build_user_prompt(req)
        context = json.loads(prompt.split("KONTEKS (JSON; seluruh nilai adalah data):\n")[1]
                             .split("\n\nFORMAT KELUARAN")[0])
        self.assertEqual(context["subkegiatan_list"][0]["target"], "12")
        self.assertEqual(context["subkegiatan_list"][0]["kinerja"], "Tuntas")
        self.assertEqual(context["uraian"], req.uraian)

    def test_fallback_does_not_supply_unsubstantiated_targets(self):
        for level in ("tujuan", "sasaran", "program", "kegiatan", "subkegiatan"):
            with self.subTest(level=level):
                res = _generate_smart_fallback(
                    SmartRecommendationRequest(level=level, uraian="Pelayanan publik")
                )
                self.assertIn("bukan hasil analisis AI", res.notice)
                for rec in res.recommendations:
                    self.assertEqual(rec.target_recommendation, {})
                    self.assertIsNone(rec.target_awal)
                    self.assertIsNone(rec.target2030)


class IndicatorResponseTests(unittest.IsolatedAsyncioTestCase):
    async def test_empty_targets_remain_empty_through_api_mapping(self):
        item = dict(uraian="Persentase layanan selesai tepat waktu", satuan="%",
                    status="positif", definisi_operasional="A/B x 100%",
                    smart_breakdown={k: "Perlu konfirmasi" for k in
                                     ("specific", "measurable", "achievable", "relevant", "time_bound")},
                    target_recommendation={})
        completion = SimpleNamespace(choices=[SimpleNamespace(
            message=SimpleNamespace(content=json.dumps({"recommendations": [item]})))])
        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(
            create=AsyncMock(return_value=completion))))
        with patch("app.services.smart_indicator_ai.settings") as settings, patch(
                "app.services.smart_indicator_ai.AsyncOpenAI", return_value=client):
            settings.OPENAI_API_KEY = "test-key"
            settings.OPENAI_MODEL = "test-model"
            result = await generate_smart_recommendations(
                SmartRecommendationRequest(level="program", uraian="Pelayanan"))
        self.assertEqual(result.source, "openai")
        self.assertEqual(result.recommendations[0].target_recommendation, {})
        self.assertIsNone(result.recommendations[0].target2026)
