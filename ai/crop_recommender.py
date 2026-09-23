import math

class CropRecommender:
    """
    Agricultural ML Crop Recommendation Engine
    Uses multi-variable environmental and soil parameters:
    Nitrogen (N), Phosphorus (P), Potassium (K), Temperature (°C),
    Humidity (%), pH (0-14), and Rainfall (mm).
    """
    
    # Agronomic profiles for major commercial & staple crops
    CROP_PROFILES = [
        {
            "crop": "Rice (Paddy)",
            "n": (60, 100), "p": (35, 60), "k": (35, 50),
            "temp": (20.0, 37.0), "humidity": (75.0, 95.0),
            "ph": (5.5, 7.2), "rainfall": (180.0, 300.0),
            "yield_acre": "22 - 28 Quintals / Acre",
            "duration": "110 - 140 Days",
            "roi": 45,
            "soil": "Clayey, Alluvial, Loamy",
            "season": "Kharif / Monsoon"
        },
        {
            "crop": "Wheat",
            "n": (80, 120), "p": (40, 60), "k": (30, 45),
            "temp": (12.0, 25.0), "humidity": (50.0, 70.0),
            "ph": (6.0, 7.5), "rainfall": (50.0, 100.0),
            "yield_acre": "18 - 24 Quintals / Acre",
            "duration": "115 - 130 Days",
            "roi": 38,
            "soil": "Well-drained Loam, Clay Loam",
            "season": "Rabi / Winter"
        },
        {
            "crop": "Cotton",
            "n": (100, 140), "p": (40, 60), "k": (40, 60),
            "temp": (22.0, 35.0), "humidity": (50.0, 75.0),
            "ph": (6.0, 8.0), "rainfall": (60.0, 110.0),
            "yield_acre": "10 - 15 Quintals / Acre",
            "duration": "150 - 180 Days",
            "roi": 52,
            "soil": "Deep Black Soil (Regur)",
            "season": "Kharif"
        },
        {
            "crop": "Maize (Corn)",
            "n": (70, 110), "p": (40, 60), "k": (30, 50),
            "temp": (18.0, 32.0), "humidity": (55.0, 80.0),
            "ph": (5.8, 7.5), "rainfall": (60.0, 120.0),
            "yield_acre": "25 - 32 Quintals / Acre",
            "duration": "90 - 110 Days",
            "roi": 42,
            "soil": "Deep Loam, Red Sandy Loam",
            "season": "Kharif / Rabi"
        },
        {
            "crop": "Tomato",
            "n": (80, 120), "p": (50, 80), "k": (60, 100),
            "temp": (18.0, 30.0), "humidity": (60.0, 85.0),
            "ph": (6.0, 7.0), "rainfall": (60.0, 130.0),
            "yield_acre": "180 - 250 Quintals / Acre",
            "duration": "90 - 120 Days",
            "roi": 65,
            "soil": "Rich Sandy Loam with High Organic Matter",
            "season": "Year-round (Kharif & Rabi)"
        },
        {
            "crop": "Potato",
            "n": (90, 130), "p": (60, 90), "k": (80, 120),
            "temp": (15.0, 24.0), "humidity": (65.0, 85.0),
            "ph": (5.2, 6.8), "rainfall": (40.0, 90.0),
            "yield_acre": "120 - 180 Quintals / Acre",
            "duration": "80 - 100 Days",
            "roi": 55,
            "soil": "Loose, friable sandy loam",
            "season": "Rabi / Winter"
        },
        {
            "crop": "Sugarcane",
            "n": (150, 250), "p": (60, 100), "k": (80, 150),
            "temp": (20.0, 38.0), "humidity": (70.0, 90.0),
            "ph": (6.5, 8.0), "rainfall": (120.0, 220.0),
            "yield_acre": "350 - 450 Quintals / Acre",
            "duration": "300 - 360 Days",
            "roi": 48,
            "soil": "Heavy Loam, Alluvial with Good Drainage",
            "season": "Perennial / Annual"
        },
        {
            "crop": "Chickpea (Gram)",
            "n": (20, 45), "p": (40, 70), "k": (20, 40),
            "temp": (14.0, 28.0), "humidity": (40.0, 65.0),
            "ph": (6.0, 7.8), "rainfall": (30.0, 70.0),
            "yield_acre": "8 - 12 Quintals / Acre",
            "duration": "95 - 110 Days",
            "roi": 35,
            "soil": "Well-aerated Sandy Loam to Clay",
            "season": "Rabi"
        }
    ]

    def predict(self, n, p, k, temp, humidity, ph, rainfall):
        """Calculates distance-weighted matching score for all crops."""
        results = []
        for profile in self.CROP_PROFILES:
            score = 0.0
            
            # Helper distance score (1.0 = exact within range, penalty for deviation)
            def calc_param_score(val, min_val, max_val, scale):
                if min_val <= val <= max_val:
                    return 1.0
                dist = min(abs(val - min_val), abs(val - max_val))
                return max(0.0, 1.0 - (dist / scale))

            s_n = calc_param_score(n, profile["n"][0], profile["n"][1], 80.0)
            s_p = calc_param_score(p, profile["p"][0], profile["p"][1], 50.0)
            s_k = calc_param_score(k, profile["k"][0], profile["k"][1], 60.0)
            s_t = calc_param_score(temp, profile["temp"][0], profile["temp"][1], 15.0)
            s_h = calc_param_score(humidity, profile["humidity"][0], profile["humidity"][1], 40.0)
            s_ph = calc_param_score(ph, profile["ph"][0], profile["ph"][1], 3.0)
            s_r = calc_param_score(rainfall, profile["rainfall"][0], profile["rainfall"][1], 150.0)
            
            # Weighted average
            total_score = (s_n * 0.15) + (s_p * 0.15) + (s_k * 0.15) + (s_t * 0.15) + (s_h * 0.1) + (s_ph * 0.15) + (s_r * 0.15)
            confidence = round(min(98.5, max(45.0, total_score * 100)), 1)
            
            results.append({
                "crop": profile["crop"],
                "confidence": confidence,
                "yield_acre": profile["yield_acre"],
                "duration": profile["duration"],
                "roi_percent": profile["roi"],
                "soil_type": profile["soil"],
                "season": profile["season"]
            })
            
        results.sort(key=lambda x: x["confidence"], reverse=True)
        top_crop = results[0]
        alternatives = results[1:3]
        
        return {
            "primary_recommendation": top_crop,
            "alternatives": alternatives,
            "soil_suitability": "Optimal" if top_crop["confidence"] >= 80 else "Moderate with Soil Amendment"
        }

