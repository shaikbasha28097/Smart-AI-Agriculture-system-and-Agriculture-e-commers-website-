class IrrigationAdvisor:
    """
    Smart Irrigation Scheduling & Water Requirement Engine.
    Computes daily water demand (litres/acre) based on crop coefficient (Kc),
    soil texture, growth stage, ambient temperature, and humidity.
    """
    
    CROP_KC = {
        "rice": {"initial": 1.15, "mid": 1.35, "late": 1.05},
        "wheat": {"initial": 0.35, "mid": 1.15, "late": 0.45},
        "cotton": {"initial": 0.45, "mid": 1.20, "late": 0.65},
        "tomato": {"initial": 0.60, "mid": 1.15, "late": 0.80},
        "potato": {"initial": 0.50, "mid": 1.15, "late": 0.75},
        "general": {"initial": 0.50, "mid": 1.00, "late": 0.70}
    }

    def calculate_water_schedule(self, crop_name, growth_stage, soil_type, temp_c=30.0, farm_size_acres=1.0):
        crop_key = crop_name.lower().split()[0] if crop_name else "general"
        kc_table = self.CROP_KC.get(crop_key, self.CROP_KC["general"])
        
        stage_key = "mid"
        if "seed" in growth_stage.lower() or "init" in growth_stage.lower() or "vegetat" in growth_stage.lower():
            stage_key = "initial"
        elif "matur" in growth_stage.lower() or "harvest" in growth_stage.lower() or "late" in growth_stage.lower():
            stage_key = "late"
            
        kc = kc_table[stage_key]
        
        # Reference Evapotranspiration (ETo mm/day estimation via temperature)
        eto = max(3.0, (float(temp_c) * 0.16) + 1.2)
        crop_water_mm = eto * kc
        
        # 1 mm of water over 1 acre = 4,047 Litres
        litres_per_acre_day = round(crop_water_mm * 4047 * float(farm_size_acres))
        
        # Soil holding adjustments
        soil_lower = soil_type.lower()
        if "sandy" in soil_lower:
            frequency = "Daily or every 2 days (Light & frequent drip cycles)"
            drip_hours = 2.5
        elif "clay" in soil_lower:
            frequency = "Every 4 to 6 days (Deep watering)"
            drip_hours = 4.0
        else: # Loamy
            frequency = "Every 3 to 4 days (Standard cycle)"
            drip_hours = 3.0
            
        return {
            "crop": crop_name,
            "growth_stage": growth_stage,
            "soil_type": soil_type,
            "crop_coefficient_kc": kc,
            "daily_evapotranspiration_mm": round(crop_water_mm, 2),
            "water_required_litres_per_day": litres_per_acre_day,
            "recommended_frequency": frequency,
            "drip_run_time_hours": drip_hours,
            "smart_advice": f"For {farm_size_acres} acre(s) of {crop_name} during {growth_stage} stage, deliver ~{litres_per_acre_day:,} litres daily via drip irrigation during early morning (6:00 AM - 8:30 AM) to minimize solar evaporation."
        }

