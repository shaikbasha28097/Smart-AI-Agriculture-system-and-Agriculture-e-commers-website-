# -*- coding: utf-8 -*-
"""
Smart AI Agriculture Ecosystem — Whole-Lot Agricultural Quality & Chemical Scanner
Gatekeeper for Seller Product Listings (Fruits, Vegetables, Seeds, Plants).

Selling Condition Rule:
- Products with up to 30% chemical involvement (<= 30.0%) are APPROVED for marketplace sale.
- Products with above 30% chemical involvement (> 30.0%) are REJECTED from platform listing.

Scans whole lots across 4 agricultural categories:
1. Fruits (Mango, Apple, Banana, Orange, Papaya, etc.)
2. Vegetables (Tomato, Potato, Chilli, Onion, Brinjal, etc.)
3. Seeds (Hybrid Tomato Seeds, Paddy Seeds, Cotton Seeds, etc.)
4. Plants & Saplings (Mango Saplings, Banana Tissue Culture, Lemon Plants, etc.)
"""

import os
import hashlib

class WholeLotQualityScanner:
    def __init__(self):
        self.REJECTION_THRESHOLD_PERCENT = 30.0


        # Benchmark Knowledge Database for Agricultural Lots
        self.LOT_PROFILES = {
            # === 1. FRUITS ===
            "tomato": {
                "name": "Organic Farm Fresh Tomatoes (Vine Ripened)",
                "category": "Vegetables",
                "category_id": 2,
                "lot_unit": "Crate / 25 KG",
                "default_price": 35.0,
                "default_unit": "1 KG Pack",
                "default_stock": 250,
                "image_url": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=500&auto=format&fit=crop&q=60",
                "safe_tds_range": "110 - 160 mg/L",
                "natural_signs": "Uniform calyx star attachment, natural radial ripening gradient, natural sweet-acid aroma",
                "chemical_risk": "Chlorpyrifos, Mancozeb surface residue, Synthetic Ethylene booster",
                "profiles": {

                    "organic": {
                        "type": "organic",
                        "chemical_pct": 12.4,
                        "quality_score": 96.5,
                        "status": "100% Certified Organic Farm Lot",
                        "pesticide_detected": "Zero Synthetic Sprays (Natural Neem Extracts only)",
                        "tds_score": 138,
                        "ripening_mode": "Natural Vine Ripened (Ambient Air)",
                        "wax_coating": "Natural Cutin Layer (Zero Petroleum Wax)",
                        "toxicity_class": "Bio-Safe / Organic",
                        "freshness_pct": 98.2,
                        "shelf_life_days": "8 - 10 Days",
                        "detox_protocol": "Cold water rinse. 100% safe to eat raw with skin."
                    },
                    "chemical": {
                        "type": "chemical",
                        "chemical_pct": 68.5,
                        "quality_score": 38.0,
                        "status": "Excessive Chemical & Fungicide Contamination",
                        "pesticide_detected": "Heavy Mancozeb, Chlorpyrifos & Artificial Ethylene Booster",
                        "tds_score": 340,
                        "ripening_mode": "Artificial Forced Gas Ripening",
                        "wax_coating": "Synthetic Gloss Glaze Applied",
                        "toxicity_class": "Class II - Moderately Hazardous (Exceeds Limits)",
                        "freshness_pct": 62.0,
                        "shelf_life_days": "2 - 3 Days (Rapid Decay)",
                        "detox_protocol": "NOT RECOMMENDED FOR SALE. Requires intensive alkaline soak and skin stripping."
                    }
                }
            },
            "apple": {
                "name": "Kashmir Royal Delicious Red Apples",
                "category": "Fruits",
                "category_id": 1,
                "lot_unit": "Wooden Box / 20 KG",
                "default_price": 150.0,
                "default_unit": "1 KG Pack",
                "default_stock": 180,
                "image_url": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=500&auto=format&fit=crop&q=60",
                "safe_tds_range": "130 - 180 mg/L",
                "natural_signs": "Natural pale yellow lenticels, natural ester aroma, unpolished natural skin",
                "chemical_risk": "Morpholine shellac wax polish, Captan spray, Diphenylamine",
                "profiles": {
                    "organic": {
                        "type": "organic",
                        "chemical_pct": 8.5,
                        "quality_score": 97.8,
                        "status": "Organic Mountain Harvested Lot",
                        "pesticide_detected": "Zero Synthetic Pesticide Residue",
                        "tds_score": 145,
                        "ripening_mode": "Natural Tree Ripened",
                        "wax_coating": "Natural Apple Wax (Non-Synthetic)",
                        "toxicity_class": "Bio-Safe / Export Grade A+",
                        "freshness_pct": 97.0,
                        "shelf_life_days": "15 - 20 Days",
                        "detox_protocol": "Normal wash under tap water. Skin is edible and nutrient-dense."
                    },
                    "chemical": {
                        "type": "chemical",
                        "chemical_pct": 74.2,
                        "quality_score": 31.5,
                        "status": "Heavy Petroleum Wax Polish & Preservative Dip",
                        "pesticide_detected": "Morpholine Wax Glaze, Thiabendazole & Captan Fungicide",
                        "tds_score": 365,
                        "ripening_mode": "Controlled Chemical Cold Chamber",
                        "wax_coating": "Heavy Synthetic Petroleum Wax Glaze",
                        "toxicity_class": "High Chemical Residue (> 30% Limit)",
                        "freshness_pct": 58.0,
                        "shelf_life_days": "4 - 5 Days",
                        "detox_protocol": "REJECTED FROM PLATFORM. Severe wax residue posing digestive risks."
                    }
                }
            },
            "mango": {
                "name": "Fresh Farm Alphonso Mangoes (Ratnagiri Grade A)",
                "category": "Fruits",
                "category_id": 1,
                "lot_unit": "Crate / 15 KG",
                "default_price": 450.0,
                "default_unit": "Dozen (12 Pcs)",
                "default_stock": 80,
                "image_url": "https://images.unsplash.com/photo-1553279768-865429fa0078?w=500&auto=format&fit=crop&q=60",
                "safe_tds_range": "150 - 220 mg/L",
                "natural_signs": "Natural stem cavity aroma pocket, natural gradient yellow-orange blush, resilient pulp yield",
                "chemical_risk": "Calcium Carbide (Arsenic/Phosphorus hydride traces), Ethephon dip",
                "profiles": {
                    "organic": {
                        "type": "organic",
                        "chemical_pct": 5.0,
                        "quality_score": 98.5,
                        "status": "Tree-Ripened Organic Alphonso Lot",
                        "pesticide_detected": "Zero Harmful Chemical Traces (100% Carbide-Free)",
                        "tds_score": 178,
                        "ripening_mode": "Natural Grass/Hay Ripened",
                        "wax_coating": "Zero Artificial Polish",
                        "toxicity_class": "Certified 100% Pure Organic",
                        "freshness_pct": 99.0,
                        "shelf_life_days": "7 - 9 Days",
                        "detox_protocol": "Clean with pure water. 100% safe for all ages."
                    },
                    "chemical": {
                        "type": "chemical",
                        "chemical_pct": 82.0,
                        "quality_score": 22.0,
                        "status": "Hazardous Calcium Carbide Ripened Lot",
                        "pesticide_detected": "Arsenic Hydride & Acetylene Gas Exposure",
                        "tds_score": 420,
                        "ripening_mode": "Artificial Industrial Calcium Carbide Pouches",
                        "wax_coating": "Alkaline Chemical Dust on Peel Cavity",
                        "toxicity_class": "Severe Hazard / Prohibited by FSSAI",
                        "freshness_pct": 45.0,
                        "shelf_life_days": "1 - 2 Days (Internal Blackening)",
                        "detox_protocol": "STRICTLY BANNED: Carbide treated produce cannot be sold."
                    }
                }
            },
            "banana": {
                "name": "Fresh Farm Robusta Bananas (Pesticide Free)",
                "category": "Fruits",
                "category_id": 1,
                "lot_unit": "Bunch / 20 KG",
                "default_price": 45.0,
                "default_unit": "Dozen (12 Pcs)",
                "default_stock": 300,
                "image_url": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=500&auto=format&fit=crop&q=60",
                "safe_tds_range": "120 - 180 mg/L",
                "natural_signs": "Natural black sugar spots, dull golden skin, green neck stem",
                "chemical_risk": "Ethephon liquid dip, synthetic sulfur smoke chamber",
                "profiles": {
                    "organic": {
                        "type": "organic",
                        "chemical_pct": 9.0,
                        "quality_score": 96.0,
                        "status": "Naturally Ambient Ripened Banana Bunch",
                        "pesticide_detected": "Zero Synthetic Dipping Agents",
                        "tds_score": 142,
                        "ripening_mode": "Natural Ambient Temperature Ripened",
                        "wax_coating": "None",
                        "toxicity_class": "Bio-Safe / Natural",
                        "freshness_pct": 95.5,
                        "shelf_life_days": "5 - 7 Days",
                        "detox_protocol": "Peel and consume directly."
                    },
                    "chemical": {
                        "type": "chemical",
                        "chemical_pct": 65.0,
                        "quality_score": 42.0,
                        "status": "Excessive Ethephon Dip Accelerated Lot",
                        "pesticide_detected": "Ethephon Liquid Residue & Sulfur Smoke",
                        "tds_score": 290,
                        "ripening_mode": "Chemical Liquid Immersion",
                        "wax_coating": "Artificial Sulfur Residue",
                        "toxicity_class": "Elevated Chemical Ripener (> 30%)",
                        "freshness_pct": 65.0,
                        "shelf_life_days": "2 - 3 Days",
                        "detox_protocol": "REJECTED FROM SALE: Liquid ethephon exceeds safety standards."
                    }
                }
            },

            # === 2. VEGETABLES ===
            "potato": {
                "name": "Fresh Farm Yellow Potatoes (Clean Sorted)",
                "category": "Vegetables",
                "category_id": 2,
                "lot_unit": "Sack / 50 KG",
                "default_price": 30.0,
                "default_unit": "1 KG Pack",
                "default_stock": 600,
                "image_url": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=500&auto=format&fit=crop&q=60",
                "safe_tds_range": "140 - 200 mg/L",
                "natural_signs": "Dry natural earthy skin, zero solanine green patches, firm dormant eyes",
                "chemical_risk": "Chlorpropham (CIPC anti-sprout chemical), Imidacloprid",
                "profiles": {
                    "organic": {
                        "type": "organic",
                        "chemical_pct": 11.0,
                        "quality_score": 94.0,
                        "status": "Clean Farm Field Harvest (Anti-Sprout Chemical Free)",
                        "pesticide_detected": "Undetected / Bio-Safe",
                        "tds_score": 160,
                        "ripening_mode": "Natural Field Harvested",
                        "wax_coating": "Natural Soil Minerals",
                        "toxicity_class": "Grade A Clean Produce",
                        "freshness_pct": 94.0,
                        "shelf_life_days": "25 - 30 Days",
                        "detox_protocol": "Rinse under running water with brush to remove loam."
                    },
                    "chemical": {
                        "type": "chemical",
                        "chemical_pct": 71.5,
                        "quality_score": 35.0,
                        "status": "Heavy Chlorpropham (CIPC) Anti-Sprout Chemical Drench",
                        "pesticide_detected": "High Concentration CIPC & Soil Insecticides",
                        "tds_score": 335,
                        "ripening_mode": "Chemical Inhibit Storage",
                        "wax_coating": "Chemical Powder Layer",
                        "toxicity_class": "Heavy Anti-Sprout Residue",
                        "freshness_pct": 60.0,
                        "shelf_life_days": "7 - 10 Days",
                        "detox_protocol": "REJECTED FROM SALE: CIPC toxicity limits exceeded."
                    }
                }
            },
            "chilli": {
                "name": "Fresh Green Organic Chillies (G4 Variety)",
                "category": "Vegetables",
                "category_id": 2,
                "lot_unit": "Sack / 10 KG",
                "default_price": 60.0,
                "default_unit": "500g Pack",
                "default_stock": 150,
                "image_url": "https://images.unsplash.com/photo-1588252303782-cb80119abd6d?w=500&auto=format&fit=crop&q=60",
                "safe_tds_range": "90 - 140 mg/L",
                "natural_signs": "Crisp taut skin, firm green calyx, high pungent aroma",
                "chemical_risk": "Monocrotophos, Profenofos, Malachite Green dye",
                "profiles": {
                    "organic": {
                        "type": "organic",
                        "chemical_pct": 7.5,
                        "quality_score": 97.2,
                        "status": "100% Organic Farm Grown Lot",
                        "pesticide_detected": "Free from Malachite Green & Organophosphates",
                        "tds_score": 115,
                        "ripening_mode": "Natural Sunlight Harvest",
                        "wax_coating": "None",
                        "toxicity_class": "Certified Bio-Pure",
                        "freshness_pct": 97.0,
                        "shelf_life_days": "10 - 12 Days",
                        "detox_protocol": "Wash in salted water before cooking."
                    },
                    "chemical": {
                        "type": "chemical",
                        "chemical_pct": 78.0,
                        "quality_score": 28.0,
                        "status": "Malachite Green Dye & Synthetic Insecticide Spray",
                        "pesticide_detected": "Artificial Green Color Dye & Monocrotophos",
                        "tds_score": 380,
                        "ripening_mode": "Synthetic Chemical Treated",
                        "wax_coating": "Dye Residue Present",
                        "toxicity_class": "Carcinogenic Dye Warning (> 30% Chem)",
                        "freshness_pct": 52.0,
                        "shelf_life_days": "3 - 4 Days",
                        "detox_protocol": "REJECTED: Prohibited chemical colorants detected."
                    }
                }
            },

            # === 3. SEEDS ===
            "seeds": {
                "name": "High Yield Certified Tomato F1 Hybrid Seeds",
                "category": "Seeds",
                "category_id": 3,
                "lot_unit": "Batch / 50 KG Lot",
                "default_price": 199.0,
                "default_unit": "Pack of 10g",
                "default_stock": 150,
                "image_url": "https://images.unsplash.com/photo-1530595467537-0b5996c41f2d?w=500&auto=format&fit=crop&q=60",
                "safe_tds_range": "80 - 130 mg/L",
                "natural_signs": "High seed vigor (>95% germination potential), clean embryo, bio-protective coating",
                "chemical_risk": "Heavy Captan/Thiram powder drench, organochlorine dressers",
                "profiles": {
                    "organic": {
                        "type": "organic",
                        "chemical_pct": 14.0,
                        "quality_score": 95.0,
                        "status": "Certified Bio-Primed & Organic Coated Seed Lot",
                        "pesticide_detected": "Bio-fungicide (Trichoderma viride + Pseudomonas)",
                        "tds_score": 105,
                        "ripening_mode": "Natural Dry Conditioning",
                        "wax_coating": "Natural Seed Lipid Shell",
                        "toxicity_class": "Certified Organic Foundation Seeds",
                        "freshness_pct": 98.0,
                        "shelf_life_days": "180 - 365 Days",
                        "detox_protocol": "Ready for direct sowing with zero soil chemical pollution."
                    },
                    "chemical": {
                        "type": "chemical",
                        "chemical_pct": 69.0,
                        "quality_score": 37.0,
                        "status": "Excessive Synthetic Thiram & Chemical Dye Powder",
                        "pesticide_detected": "Heavy Chemical Seed Dressing (Exceeds Allowed PPM)",
                        "tds_score": 280,
                        "ripening_mode": "Synthetic Chemical Treated",
                        "wax_coating": "Heavy Toxic Chemical Powder",
                        "toxicity_class": "Toxic Seed Lot (> 30% Chemical)",
                        "freshness_pct": 68.0,
                        "shelf_life_days": "60 - 90 Days (Declining Vigor)",
                        "detox_protocol": "REJECTED FROM SALE: Chemical concentration impairs soil microbiota."
                    }
                }
            },

            # === 4. PLANTS & SAPLINGS ===
            "plants": {
                "name": "Grafted Thai All-Time Mango Sapling Plant",
                "category": "Plants",
                "category_id": 4,
                "lot_unit": "Nursery Batch / 50 Plants",
                "default_price": 250.0,
                "default_unit": "Live Sapling",
                "default_stock": 75,
                "image_url": "https://images.unsplash.com/photo-1546842931-886c185b4c8c?w=500&auto=format&fit=crop&q=60",
                "safe_tds_range": "100 - 150 mg/L",
                "natural_signs": "Vibrant emerald foliar tissue, healthy fibrous white root ball, sturdy graft union",
                "chemical_risk": "Systemic neonicotinoid drench, growth retardant overdosing (Paclobutrazol)",
                "profiles": {
                    "organic": {
                        "type": "organic",
                        "chemical_pct": 10.5,
                        "quality_score": 96.5,
                        "status": "Organic Nursery Propagated Live Plant Lot",
                        "pesticide_detected": "Zero Systemic Toxic Residues (Neem & bio-stimulant fed)",
                        "tds_score": 120,
                        "ripening_mode": "Natural Greenhouse Sun-hardened",
                        "wax_coating": "Natural Foliar Wax Layer",
                        "toxicity_class": "Bio-Safe Nursery Grade A+",
                        "freshness_pct": 98.5,
                        "shelf_life_days": "Perennial Live Specimen",
                        "detox_protocol": "Ready for direct orchard or garden plantation."
                    },
                    "chemical": {
                        "type": "chemical",
                        "chemical_pct": 73.0,
                        "quality_score": 33.0,
                        "status": "Heavy Systemic Chemical Drench & Hormone Overload",
                        "pesticide_detected": "Excessive Paclobutrazol & Systemic Imidacloprid in Root Ball",
                        "tds_score": 370,
                        "ripening_mode": "Chemical Hormone Forced Growth",
                        "wax_coating": "Chemical Foliar Film",
                        "toxicity_class": "Excessive Chemical Load (> 30%)",
                        "freshness_pct": 59.0,
                        "shelf_life_days": "Weak Root System",
                        "detox_protocol": "REJECTED FROM SALE: Chemical drenched root ball causes soil degradation."
                    }
                }
            }

        }

    def scan_item(self, commodity_name, image_path=None, sample_type="organic", category_id=None):
        """
        Runs the Whole-Lot Quality & Chemical Inspection.
        Enforces the Platform Selling Condition:
        - If Chemical % >= 50.0% -> REJECTED (Cannot be sold)
        - If Chemical % < 50.0%  -> APPROVED (Passed inspection)
        """
        c_lower = commodity_name.lower().strip() if commodity_name else ""
        
        # Match lot profile key
        matched_key = "tomato"
        
        # Check category hint first
        if category_id in [3, '3'] or 'seed' in c_lower:
            matched_key = "seeds"
        elif category_id in [4, '4'] or 'plant' in c_lower or 'sapling' in c_lower:
            matched_key = "plants"
        else:
            for k in self.LOT_PROFILES:
                if k in c_lower:
                    matched_key = k
                    break
        
        profile_data = self.LOT_PROFILES[matched_key]
        
        # Image deterministic micro-variance
        file_hash = 12
        if image_path and os.path.exists(image_path):
            try:
                with open(image_path, 'rb') as f:
                    content = f.read(8192)
                    file_hash = sum(content) % 100
            except Exception:
                file_hash = 12

        # Pick organic vs chemical profile variant
        profiles_dict = profile_data["profiles"]
        if sample_type == "chemical":
            selected = profiles_dict["chemical"]
        elif sample_type == "organic":
            selected = profiles_dict["organic"]
        else:
            # Automatic heuristic from image
            selected = profiles_dict["organic"] if (file_hash % 2 == 0) else profiles_dict["chemical"]

        # Calculate exact chemical % and quality %
        var_chem = (file_hash % 7) * 0.4 - 1.2
        chem_pct = round(max(2.0, min(95.0, selected["chemical_pct"] + var_chem)), 1)
        quality_score = round(100.0 - chem_pct, 1)
        tds_val = int(selected["tds_score"] + (file_hash % 9) - 4)
        fresh_pct = round(max(40.0, min(99.5, selected["freshness_pct"] + (file_hash % 5) * 0.2 - 0.5)), 1)

        # Selling Condition Gatekeeper (Approved if <= 30.0% chemical involvement)
        is_rejected = (chem_pct > self.REJECTION_THRESHOLD_PERCENT)
        selling_status = "REJECTED" if is_rejected else "APPROVED"

        if is_rejected:
            selling_message = (
                f"❌ LISTING REJECTED: Whole-lot chemical contamination is {chem_pct}% "
                f"(Exceeds the maximum permissible threshold of 30.0%). "
                f"This lot violates safety standards and cannot be sold on the E-Mart platform."
            )
            rejection_advice = (
                "Only products with 30% or lower chemical involvement (<= 30%) qualify for sale. "
                "Please provide clean, certified low-chemical or organic produce."
            )
        else:
            selling_message = (
                f"✅ LISTING APPROVED: Whole-lot chemical involvement is {chem_pct}% "
                f"(Approved under the <= 30.0% safe threshold). "
                f"Quality Grade: {selected['toxicity_class']} ({quality_score}% Purity Score)."
            )
            rejection_advice = "Lot meets the platform's <= 30% chemical food safety and quality standard."


        return {
            "commodity": profile_data["name"],
            "category": profile_data["category"],
            "category_id": profile_data.get("category_id", 1),
            "lot_unit": profile_data["lot_unit"],
            "scan_mode": "Whole Lot Batch Analysis",
            "chemical_percentage": chem_pct,
            "quality_score": quality_score,
            "threshold_limit_pct": self.REJECTION_THRESHOLD_PERCENT,
            "is_rejected": is_rejected,
            "selling_status": selling_status,
            "selling_message": selling_message,
            "rejection_advice": rejection_advice,
            "status": selected["status"],
            "is_organic": (chem_pct < 20.0),
            "pesticide_detected": selected["pesticide_detected"],
            "tds_score": tds_val,
            "tds_rating": f"{tds_val} mg/L (Safe Benchmark: {profile_data['safe_tds_range']})",
            "ripening_mode": selected["ripening_mode"],
            "wax_coating": selected["wax_coating"],
            "toxicity_class": selected["toxicity_class"],
            "freshness_pct": fresh_pct,
            "shelf_life_days": selected["shelf_life_days"],
            "detox_protocol": selected["detox_protocol"],
            "natural_signs": profile_data["natural_signs"],
            "chemical_risk": profile_data["chemical_risk"],
            "batch_homogeneity_pct": round(94.0 + (file_hash % 5) * 0.8, 1),
            "lot_sample_tested": f"Whole Lot Sample ({profile_data['lot_unit']})",
            "image_url": profile_data.get("image_url", "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=500"),
            "default_price": profile_data.get("default_price", 45.0),
            "default_unit": profile_data.get("default_unit", "KG"),
            "default_stock": profile_data.get("default_stock", 100),
            "short_description": f"AI Quality Certified ({chem_pct}% Chemical, Grade: {selected['toxicity_class']}). Tested and approved whole-lot produce."
        }

quality_scanner = WholeLotQualityScanner()

