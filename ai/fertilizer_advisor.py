class FertilizerAdvisor:
    """
    Expert Soil Nutrient & Fertilizer Dosage Recommendation Engine.
    Analyzes N-P-K deficiency, pH levels, and crop growth stage to calculate
    both organic amendments and chemical fertilizer dosage per acre.
    """
    
    STANDARD_NPK_TARGETS = {
        "rice": {"n": 100, "p": 50, "k": 50},
        "wheat": {"n": 120, "p": 60, "k": 40},
        "cotton": {"n": 120, "p": 60, "k": 60},
        "maize": {"n": 120, "p": 60, "k": 40},
        "tomato": {"n": 100, "p": 80, "k": 80},
        "potato": {"n": 120, "p": 80, "k": 100},
        "general": {"n": 100, "p": 50, "k": 50}
    }

    def analyze(self, crop_name, current_n, current_p, current_k, ph=6.5, farm_size_acres=1.0):
        crop_key = crop_name.lower().split()[0] if crop_name else "general"
        target = self.STANDARD_NPK_TARGETS.get(crop_key, self.STANDARD_NPK_TARGETS["general"])
        
        diff_n = max(0, target["n"] - float(current_n))
        diff_p = max(0, target["p"] - float(current_p))
        diff_k = max(0, target["k"] - float(current_k))
        
        # Calculate chemical fertilizer equivalents (Urea ~46% N, DAP ~18% N + 46% P2O5, MOP ~60% K2O)
        urea_kg = round((diff_n * 2.17) * float(farm_size_acres), 1)
        dap_kg = round((diff_p * 2.17) * float(farm_size_acres), 1)
        mop_kg = round((diff_k * 1.66) * float(farm_size_acres), 1)
        
        # Calculate organic alternatives
        vermicompost_ton = round(1.5 * float(farm_size_acres), 1)
        neem_cake_kg = round(100 * float(farm_size_acres), 1)
        bio_npk_litres = round(1.0 * float(farm_size_acres), 1)
        
        soil_status = "Optimal"
        if ph < 5.8:
            ph_advisory = "Soil is Acidic (pH < 5.8). Apply Agricultural Lime (Calcium Carbonate) @ 200 kg/acre."
        elif ph > 7.8:
            ph_advisory = "Soil is Alkaline/Saline (pH > 7.8). Apply Gypsum @ 250 kg/acre and green manuring (Dhaincha)."
        else:
            ph_advisory = "Soil pH is in the optimal nutrient absorption range (6.0 - 7.5)."
            
        return {
            "crop": crop_name,
            "target_npk": target,
            "deficit": {"n": round(diff_n, 1), "p": round(diff_p, 1), "k": round(diff_k, 1)},
            "soil_ph_status": ph_advisory,
            "organic_schedule": [
                f"Basal application: Apply {vermicompost_ton} Tons of well-decomposed Vermicompost + {neem_cake_kg} KG Neem Cake per {farm_size_acres} acre.",
                f"Bio-fertilizer inoculation: Apply Bio-NPK liquid consortia ({bio_npk_litres} Litre) mixed with moist FYM during seed bed preparation.",
                "Foliar bio-spray: Spray fermented Jeevamrit or Panchagavya (3% dilution) at 15-day intervals."
            ],
            "chemical_schedule": [
                f"Basal dose: DAP ({dap_kg} KG) + MOP ({mop_kg} KG) applied along rows before sowing/transplanting.",
                f"Split Nitrogen: Apply Urea ({urea_kg} KG total) in 3 equal splits: 1/3 at basal, 1/3 at active tillering/vegetative, and 1/3 at panicle initiation.",
                "Micronutrients: Zinc Sulphate 21% @ 10 kg/acre if soil shows Zn deficiency."
            ],
            "linked_products": [
                {"id": 4, "name": "Water Soluble NPK 19-19-19 Fertilizer", "price": 180.00},
                {"id": 2, "name": "Pure Cold-Pressed Neem Oil Spray", "price": 280.00}
            ]
        }

