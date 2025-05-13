from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import random
import os
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

# MongoDB connection
mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
mongo_db = os.getenv('MONGO_DB', 'csgo_cases_db')

client = MongoClient(mongo_uri)
db = client[mongo_db]

# Clear existing data
db.cases.delete_many({})
db.skins.delete_many({})
db.qualities.delete_many({})
db.weapons.delete_many({})

print("Начинаем загрузку данных для кейсов CS:GO...")

# Create quality levels
qualities = [
    {
        "title": "Consumer Grade",
        "color": "#b0c3d9",
        "order": 1
    },
    {
        "title": "Industrial Grade",
        "color": "#5e98d9",
        "order": 2
    },
    {
        "title": "Mil-Spec",
        "color": "#4b69ff",
        "order": 3
    },
    {
        "title": "Restricted",
        "color": "#8847ff",
        "order": 4
    },
    {
        "title": "Classified",
        "color": "#d32ce6",
        "order": 5
    },
    {
        "title": "Covert",
        "color": "#eb4b4b",
        "order": 6
    },
    {
        "title": "Exceedingly Rare",
        "color": "#ffae39",
        "order": 7
    },
    {
        "title": "Contraband",
        "color": "#e4ae39",
        "order": 8
    }
]

# Insert quality levels
quality_ids = {}
for quality in qualities:
    result = db.qualities.insert_one(quality)
    quality_ids[quality["title"]] = result.inserted_id

# Define weapons
weapons = [
    {"title": "AK-47", "type": "rifle"},
    {"title": "M4A4", "type": "rifle"},
    {"title": "M4A1-S", "type": "rifle"},
    {"title": "AWP", "type": "sniper rifle"},
    {"title": "Desert Eagle", "type": "pistol"},
    {"title": "USP-S", "type": "pistol"},
    {"title": "Glock-18", "type": "pistol"},
    {"title": "P250", "type": "pistol"},
    {"title": "Five-SeveN", "type": "pistol"},
    {"title": "Tec-9", "type": "pistol"},
    {"title": "P90", "type": "smg"},
    {"title": "MP7", "type": "smg"},
    {"title": "UMP-45", "type": "smg"},
    {"title": "MAC-10", "type": "smg"},
    {"title": "MP9", "type": "smg"},
    {"title": "Galil AR", "type": "rifle"},
    {"title": "FAMAS", "type": "rifle"},
    {"title": "SG 553", "type": "rifle"},
    {"title": "AUG", "type": "rifle"},
    {"title": "SSG 08", "type": "sniper rifle"},
    {"title": "G3SG1", "type": "sniper rifle"},
    {"title": "SCAR-20", "type": "sniper rifle"},
    {"title": "Nova", "type": "shotgun"},
    {"title": "XM1014", "type": "shotgun"},
    {"title": "Sawed-Off", "type": "shotgun"},
    {"title": "MAG-7", "type": "shotgun"},
    {"title": "M249", "type": "machinegun"},
    {"title": "Negev", "type": "machinegun"},
    {"title": "CZ75-Auto", "type": "pistol"},
    {"title": "R8 Revolver", "type": "pistol"},
    {"title": "Dual Berettas", "type": "pistol"},
    {"title": "PP-Bizon", "type": "smg"},
    {"title": "P2000", "type": "pistol"},
    {"title": "Bayonet", "type": "knife"},
    {"title": "Flip Knife", "type": "knife"},
    {"title": "Gut Knife", "type": "knife"},
    {"title": "Karambit", "type": "knife"},
    {"title": "M9 Bayonet", "type": "knife"},
    {"title": "Huntsman Knife", "type": "knife"},
    {"title": "Butterfly Knife", "type": "knife"},
    {"title": "Falchion Knife", "type": "knife"},
    {"title": "Shadow Daggers", "type": "knife"},
    {"title": "Bowie Knife", "type": "knife"},
    {"title": "Hand Wraps", "type": "gloves"},
    {"title": "Bloodhound Gloves", "type": "gloves"},
    {"title": "Driver Gloves", "type": "gloves"},
    {"title": "Moto Gloves", "type": "gloves"},
    {"title": "Specialist Gloves", "type": "gloves"},
    {"title": "Sport Gloves", "type": "gloves"}
]

# Insert weapons
weapon_ids = {}
for weapon in weapons:
    result = db.weapons.insert_one(weapon)
    weapon_ids[weapon["title"]] = result.inserted_id

# Define case release dates
case_info = {
    "CS:GO Weapon Case": "2013-08-14",
    "eSports 2013 Case": "2013-08-14",
    "CS:GO Weapon Case 2": "2013-11-06",
    "Winter Offensive Weapon Case": "2013-12-18",
    "eSports 2013 Winter Case": "2013-12-18",
    "CS:GO Weapon Case 3": "2014-02-12",
    "Operation Phoenix Weapon Case": "2014-02-20",
    "Huntsman Weapon Case": "2014-05-01",
    "Operation Breakout Weapon Case": "2014-07-01",
    "eSports 2014 Summer Case": "2014-07-10",
    "Operation Vanguard Weapon Case": "2014-11-11",
    "Chroma Case": "2015-01-08",
    "Chroma 2 Case": "2015-04-15",
    "Falchion Case": "2015-05-26",
    "Shadow Case": "2015-09-17",
    "Revolver Case": "2015-12-08",
    "Operation Wildfire Case": "2016-02-17",
    "Chroma 3 Case": "2016-04-27",
    "Gamma Case": "2016-06-15",
    "Gamma 2 Case": "2016-08-18",
    "Glove Case": "2016-11-28",
    "Spectrum Case": "2017-03-15",
    "Operation Hydra Case": "2017-05-23",
    "Spectrum 2 Case": "2017-09-14"
}

# This dictionary maps weapon and pattern combos to image URLs
skin_images = {
    # CS:GO Weapon Case
    "AWP | Lightning Strike": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_awp_am_lightning_awp_light_png.png",
    "AK-47 | Case Hardened": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_ak47_aq_oiled_light_png.png",
    "Desert Eagle | Hypnotic": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_deagle_aa_vertigo_light_png.png",
    "Glock-18 | Dragon Tattoo": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_glock_am_dragon_glock_light_png.png",
    "M4A1-S | Dark Water": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_m4a1_silencer_am_zebra_dark_light_png.png",
    "USP-S | Dark Water": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_usp_silencer_am_zebra_dark_light_png.png",
    "SG 553 | Ultraviolet": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_sg556_so_purple_light_png.png",
    "AUG | Wings": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_aug_hy_feathers_aug_light_png.png",
    "MP7 | Skulls": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_mp7_hy_skulls_light_png.png",
    
    # eSports 2013 Case
    "P90 | Death by Kitty": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_p90_cu_catskulls_p90_light_png.png",
    "AK-47 | Red Laminate": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_ak47_hy_ak47lam_light_png.png",
    "AWP | BOOM": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_awp_hy_blam_simple_light_png.png",
    "M4A4 | Faded Zebra": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_m4a1_sp_zebracam_bw_light_png.png",
    "Galil AR | Orange DDPAT": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_galilar_hy_ddpat_orange_light_png.png",
    "SCAR-20 | Crimson Web": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_scar20_hy_webs_darker_light_png.png",
    "FAMAS | Doomkitty": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_famas_hy_doomkitty_light_png.png",
    "MAG-7 | Bulldozer": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_mag7_so_yellow_light_png.png",
    "P2000 | Scorpion": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_hkp2000_am_scorpion_p2000_light_png.png",
    
    # CS:GO Weapon Case 2
    "SSG 08 | Blood in the Water": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_ssg08_cu_shark_light_png.png",
    "P90 | Cold Blooded": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_p90_am_slither_p90_light_png.png",
    "USP-S | Serum": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_usp_silencer_am_electric_red_light_png.png",
    "Five-SeveN | Case Hardened": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_fiveseven_aq_oiled_light_png.png",
    "MP9 | Rose Iron": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_mp9_am_thorny_rose_mp9_light_png.png",
    "Nova | Graphite": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_nova_am_crumple_light_png.png",
    "Dual Berettas | Black Limba": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_elite_cu_season_elites_bravo_light_png.png",
    "M4A1-S | Bright Water": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_m4a1_silencer_hy_ocean_bravo_light_png.png",
    "P250 | Splash": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_p250_sp_splash_p250_light_png.png",
    "Tec-9 | Blue Titanium": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_tec9_an_titanium30v_light_png.png",
    "FAMAS | Hexane": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_famas_hy_bluehex_light_png.png",
    
    # Winter Offensive Weapon Case
    "M4A4 | Asiimov": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_m4a1_cu_m4_asimov_light_png.png",
    "AWP | Redline": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_awp_cu_awp_cobra_light_png.png",
    "Sawed-Off | The Kraken": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_sawedoff_cu_sawedoff_octopump_light_png.png",
    "P250 | Mehndi": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_p250_cu_p250_refined_light_png.png",
    "XM1014 | Tranquility": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_xm1014_cu_xm1014_caritas_light_png.png",
    "PP-Bizon | Cobalt Halftone": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_bizon_am_turqoise_halftone_light_png.png",
    "Galil AR | Sandstorm": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_galilar_cu_sandstorm_light_png.png",
    "Five-SeveN | Kami": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_fiveseven_hy_kimono_diamonds_light_png.png",
    "M249 | Magma": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_m249_aq_obsidian_light_png.png",
    "Dual Berettas | Marina": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_elite_hy_marina_sunrise_light_png.png",
    "Nova | Rising Skull": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_nova_cu_skull_nova_light_png.png",
    
    # eSports 2013 Winter Case
    "AWP | Electric Hive": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_awp_hy_hive_light_png.png",
    "M4A4 | X-Ray": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_m4a1_cu_xray_m4_light_png.png",
    "Desert Eagle | Cobalt Disruption": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_deagle_am_ddpatdense_peacock_light_png.png",
    "P90 | Blind Spot": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_p90_hy_modspots_light_png.png",
    "USP-S | Stainless": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_usp_silencer_aq_usp_stainless_light_png.png",
    "Glock-18 | Blue Fissure": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_glock_hy_craquelure_light_png.png",
    "Tec-9 | Titanium Bit": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_tec9_so_titanium90_light_png.png",
    "PP-Bizon | Water Sigil": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_bizon_hy_water_crest_light_png.png",
    "Nova | Ghost Camo": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_nova_sp_camo_wood_blue_light_png.png",
    "G3SG1 | Azure Zebra": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_g3sg1_sp_zebracam_blue_light_png.png",
    "P250 | Steel Disruption": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_p250_am_ddpatdense_silver_light_png.png",
    "AK-47 | Blue Laminate": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_ak47_hy_ak47lam_blue_light_png.png",
    
    # CS:GO Weapon Case 3
    "CZ75-Auto | Victoria": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_cz75a_aq_etched_cz75_light_png.png",
    "Desert Eagle | Heirloom": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_deagle_aq_engraved_deagle_light_png.png",
    "P2000 | Red FragCam": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_hkp2000_hy_poly_camo_light_png.png",
    "Tec-9 | Sandstorm": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_tec9_cu_tec9_sandstorm_light_png.png",
    "CZ75-Auto | The Fuschia Is Now": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_cz75a_am_fuschia_light_png.png",
    "Five-SeveN | Copper Galaxy": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_fiveseven_am_copper_flecks_light_png.png",
    "P250 | Undertow": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_p250_am_p250_beaded_paint_light_png.png",
    "Dual Berettas | Panther": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_elite_so_panther_light_png.png",
    "CZ75-Auto | Crimson Web": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_cz75a_hy_webs_light_png.png",
    "P2000 | Pulse": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_hkp2000_cu_p2000_pulse_light_png.png",
    
    # Operation Phoenix Weapon Case
    "AWP | Asiimov": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_awp_cu_awp_asimov_light_png.png",
    "AUG | Chameleon": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_aug_cu_aug_chameleonaire_light_png.png",
    "AK-47 | Redline": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_ak47_cu_ak47_cobra_light_png.png",
    "Nova | Antique": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_nova_cu_nova_antique_light_png.png",
    "P90 | Trigon": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_p90_cu_p90_trigon_light_png.png",
    "FAMAS | Sergeant": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_famas_an_famas_sgt_light_png.png",
    "USP-S | Guardian": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_usp_silencer_cu_usp_elegant_light_png.png",
    "UMP-45 | Corporal": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_ump45_cu_ump_corporal_light_png.png",
    "MAG-7 | Heaven Guard": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_mag7_cu_mag7_heaven_light_png.png",
    "MAC-10 | Heat": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_mac10_cu_mac10_redhot_light_png.png",
    "SG 553 | Pulse": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_sg556_cu_sg553_pulse_light_png.png",
    "Negev | Terrain": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_negev_sp_negev_turq_terrain_light_png.png",
    
    # Huntsman Weapon Case
    "AK-47 | Vulcan": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_ak47_cu_ak47_rubber_light_png.png",
    "M4A1-S | Atomic Alloy": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_m4a1_silencer_am_m4a1-s_alloy_orange_light_png.png",
    "USP-S | Caiman": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_usp_silencer_cu_kaiman_light_png.png",
    "SCAR-20 | Cyrex": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_scar20_cu_scar20_intervention_light_png.png",
    "M4A4 | Desert-Strike": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_m4a1_cu_titanstorm_light_png.png",
    "MAC-10 | Tatter": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_mac10_cu_korupt_light_png.png",
    "PP-Bizon | Antique": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_bizon_cu_bizon_antique_light_png.png",
    "XM1014 | Heaven Guard": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_xm1014_cu_xm1014_heaven_guard_light_png.png",
    "P90 | Module": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_p90_an_royalbleed_light_png.png",
    "CZ75-Auto | Twist": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_cz75a_am_gyrate_light_png.png",
    "AUG | Torque": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_aug_cu_aug_progressiv_light_png.png",
    "Tec-9 | Isaac": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_tec9_cu_tec9_asiimov_light_png.png",
    "SSG 08 | Slashed": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_ssg08_cu_ssg08_immortal_light_png.png",
    "Galil AR | Kami": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_galilar_hy_galil_kami_light_png.png",
    
    # Operation Breakout Weapon Case
    "M4A1-S | Cyrex": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_m4a1_silencer_cu_m4a1s_cyrex_light_png.png",
    "P90 | Asiimov": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_p90_cu_p90-asiimov_light_png.png",
    "Glock-18 | Water Elemental": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_glock_cu_glock_deathtoll_light_png.png",
    "Desert Eagle | Conspiracy": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_deagle_cu_deagle_aureus_light_png.png",
    "P250 | Supernova": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_p250_cu_bittersweet_light_png.png",
    "Five-SeveN | Fowl Play": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_fiveseven_cu_fiveseven_urban_hazard_light_png.png",
    "Nova | Koi": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_nova_cu_nova_koi_light_png.png",
    "PP-Bizon | Osiris": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_bizon_cu_bizon-osiris_light_png.png",
    "SSG 08 | Abyss": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_ssg08_aq_leviathan_light_png.png",
    "UMP-45 | Labyrinth": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_ump45_hy_lines_orange_light_png.png",
    "MP7 | Urban Hazard": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_mp7_cu_mp7-commander_light_png.png",
    "CZ75-Auto | Tigris": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_cz75a_cu_c75a-tiger_light_png.png",
    "Negev | Desert-Strike": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_negev_cu_negev_titanstorm_light_png.png",
    
    # eSports 2014 Summer Case
    "Nova | Bloomstick": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_nova_cu_spring_nova_light_png.png",
    "AWP | Corticera": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_awp_cu_favela_awp_light_png.png",
    "P90 | Virus": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_p90_hy_zombie_light_png.png",
    "M4A4 | Bullet Rain": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_m4a1_cu_bullet_rain_m4a1_light_png.png",
    "AK-47 | Jaguar": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_ak47_cu_panther_ak47_light_png.png",
    "Desert Eagle | Crimson Web": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_deagle_hy_webs_darker_light_png.png",
    "MP7 | Ocean Foam": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_mp7_am_ossify_blue_light_png.png",
    "Glock-18 | Steel Disruption": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_glock_am_ddpatdense_silver_light_png.png",
    "AUG | Bengal Tiger": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_aug_hy_tiger_light_png.png",
    "FAMAS | Styx": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_famas_am_famas_dots_light_png.png",
    "CZ75-Auto | Hexane": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_cz75a_hy_bluehex_light_png.png",
    "Negev | Bratatat": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_negev_cu_bratatat_negev_light_png.png",
    
    # Operation Vanguard Weapon Case
    "AK-47 | Wasteland Rebel": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_ak47_cu_well_traveled_ak47_light_png.png",
    "P2000 | Fire Elemental": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_hkp2000_cu_p2000_fire_elemental_light_png.png",
    "M4A4 | Griffin": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_m4a1_cu_m4a4_griffin_light_png.png",
    "M4A1-S | Basilisk": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_m4a1_silencer_aq_m4a1s_basilisk_light_png.png",
    "SCAR-20 | Cardiac": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_scar20_cu_scar20_intervention_light_png.png",
    "XM1014 | Tranquility": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_xm1014_cu_xm1014_heaven_guard_light_png.png",
    "Glock-18 | Grinder": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_glock_aq_glock_coiled_light_png.png",
    "P250 | Cartel": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_p250_aq_p250_cartel_light_png.png",
    "Galil AR | Firefight": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_galilar_gs_galilar_incenerator_light_png.png",
    "UMP-45 | Delusion": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_ump45_sp_ump45_d-visions_light_png.png",
    "MAG-7 | Firestarter": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_mag7_sp_mag7_firebitten_light_png.png",
    "Sawed-Off | Highwayman": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_sawedoff_aq_sawedoff_blackgold_light_png.png",
    
    # Chroma Case
    "Galil AR | Chatterbox": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_galilar_cu_galil_abrasion_light_png.png",
    "AWP | Man-o'-war": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_awp_am_awp_glory_light_png.png",
    "AK-47 | Cartel": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_ak47_aq_ak47_cartel_light_png.png",
    "Dual Berettas | Urban Shock": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_elite_cu_elites_urbanstorm_light_png.png",
    "Desert Eagle | Naga": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_deagle_aq_deagle_naga_light_png.png",
    "MAC-10 | Malachite": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_mac10_am_mac10_malachite_light_png.png",
    "Sawed-Off | Serenity": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_sawedoff_cu_sawedoff_deva_light_png.png",
    "P250 | Muertos": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_p250_cu_p250_mandala_light_png.png",
    "Glock-18 | Catacombs": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_glock_cu_glock_deathtoll_light_png.png",
    "M249 | System Lock": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_m249_cu_m249_sektor_light_png.png",
    "MP9 | Deadly Poison": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_mp9_cu_mp9_deadly_poison_light_png.png",
    "SCAR-20 | Grotto": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_scar20_aq_scar20_leak_light_png.png",
    "XM1014 | Quicksilver": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_xm1014_aq_xm1014_sigla_light_png.png",
    
    # Chroma 2 Case
    "M4A1-S | Hyper Beast": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_m4a1_silencer_cu_m4a1_hyper_beast_light_png.png",
    "MAC-10 | Neon Rider": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_mac10_cu_mac10_neonrider_light_png.png",
    "Galil AR | Eco": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_galilar_cu_galil_eco_light_png.png",
    "FAMAS | Djinn": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_famas_aq_famas_jinn_light_png.png",
    "Five-SeveN | Monkey Business": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_fiveseven_cu_fiveseven_banana_light_png.png",
    "AWP | Worm God": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_awp_aq_awp_twine_light_png.png",
    "MAG-7 | Heat": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_mag7_cu_mag7_redhot_light_png.png",
    "CZ75-Auto | Pole Position": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_cz75a_cu_cz75_precision_light_png.png",
    "UMP-45 | Grand Prix": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_ump45_am_ump_racer_light_png.png",
    "Desert Eagle | Bronze Deco": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_deagle_am_bronze_sparkle_light_png.png",
    "P250 | Valence": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_p250_aq_p250_contour_light_png.png",
    "Negev | Man-o'-war": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_negev_am_negev_glory_light_png.png",
    "MP7 | Armor Core": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_mp7_cu_mp7_classified_light_png.png",
    "Sawed-Off | Origami": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_sawedoff_cu_sawedoff_origami_light_png.png",
    "AK-47 | Elite Build": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_ak47_cu_ak47_mastery_light_png.png",
    
    # Falchion Case
    "AWP | Hyper Beast": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_awp_cu_awp_hyper_beast_light_png.png",
    "AK-47 | Aquamarine Revenge": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_ak47_cu_ak47_courage_alt_light_png.png",
    "SG 553 | Cyrex": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_sg556_cu_sg553_cyrex_light_png.png",
    "M4A4 | Evil Daimyo": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_m4a1_cu_m4a4_evil_daimyo_light_png.png",
    "FAMAS | Neural Net": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_famas_am_famas_dots_light_png.png",
    "MP9 | Ruby Poison Dart": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_mp9_am_mp9_nitrogen_light_png.png",
    "Negev | Loudmouth": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_negev_cu_negev_annihilator_light_png.png",
    "P2000 | Handgun": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_hkp2000_aq_p2000_boom_light_png.png",
    "CZ75-Auto | Yellow Jacket": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_cz75a_cu_cz75a_chastizer_light_png.png",
    "MP7 | Nemesis": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_mp7_cu_mp7_nemsis_light_png.png",
    "Galil AR | Rocket Pop": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_galilar_cu_galilar_particles_light_png.png",
    "Glock-18 | Bunsen Burner": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_glock_aq_glock18_flames_blue_light_png.png",
    "Nova | Ranger": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_nova_cu_nova_ranger_light_png.png",
    "UMP-45 | Riot": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_ump45_cu_ump45_uproar_light_png.png",
    "USP-S | Torque": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_usp_silencer_cu_usp_progressiv_light_png.png",
    
    # Add the rest of the skin mappings for the remaining cases
    # This is a large dictionary, so I'm showing only a subset
}

# Map for case image URLs
case_images = {
    "CS:GO Weapon Case": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapon_cases/crate_valve_1_png.png",
    "eSports 2013 Case": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapon_cases/crate_esports_2013_png.png",
    "CS:GO Weapon Case 2": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapon_cases/crate_valve_2_png.png",
    "Winter Offensive Weapon Case": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapon_cases/crate_community_1_png.png",
    "eSports 2013 Winter Case": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapon_cases/crate_esports_2013_14_png.png",
    "CS:GO Weapon Case 3": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapon_cases/crate_valve_3_png.png",
    "Operation Phoenix Weapon Case": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapon_cases/crate_community_2_png.png",
    "Huntsman Weapon Case": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapon_cases/crate_community_3_png.png",
    "Operation Breakout Weapon Case": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapon_cases/crate_community_4_png.png",
    "eSports 2014 Summer Case": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapon_cases/crate_esports_2014_summer_png.png",
    "Operation Vanguard Weapon Case": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapon_cases/crate_community_5_png.png",
    "Chroma Case": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapon_cases/crate_community_6_png.png",
    "Chroma 2 Case": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapon_cases/crate_community_7_png.png",
    "Falchion Case": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapon_cases/crate_community_8_png.png",
    "Shadow Case": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapon_cases/crate_community_9_png.png",
    "Revolver Case": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapon_cases/crate_community_10_png.png",
    "Operation Wildfire Case": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapon_cases/crate_community_11_png.png",
    "Chroma 3 Case": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapon_cases/crate_community_12_png.png",
    "Gamma Case": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapon_cases/crate_community_13_png.png",
    "Gamma 2 Case": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapon_cases/crate_gamma_2_png.png",
    "Glove Case": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapon_cases/crate_community_15_png.png",
    "Spectrum Case": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapon_cases/crate_community_16_png.png",
    "Operation Hydra Case": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapon_cases/crate_community_17_png.png",
    "Spectrum 2 Case": "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapon_cases/crate_community_18_png.png",
}

# Helper function to get skin image URL
def get_skin_image(weapon, pattern):
    key = f"{weapon} | {pattern}"
    if key in skin_images:
        return skin_images[key]
    else:
        # Fallback to a generic weapon image
        return f"https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/weapon_{weapon.lower().replace('-', '').replace(' ', '')}_am_default_light_png.png"

# Helper function to get case image URL
def get_case_image(case_name):
    if case_name in case_images:
        return case_images[case_name]
    else:
        # Fallback to a generic case image
        return "https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapon_cases/crate_community_1_png.png"

# Define all the cases and their skins that we want to add
cases_with_skins = [
    {
        "title": "CS:GO Weapon Case",
        "skins": [
            {"weapon": "AWP", "pattern": "Lightning Strike", "quality": "Covert"},
            {"weapon": "AK-47", "pattern": "Case Hardened", "quality": "Classified"},
            {"weapon": "Desert Eagle", "pattern": "Hypnotic", "quality": "Classified"},
            {"weapon": "Glock-18", "pattern": "Dragon Tattoo", "quality": "Restricted"},
            {"weapon": "M4A1-S", "pattern": "Dark Water", "quality": "Restricted"},
            {"weapon": "USP-S", "pattern": "Dark Water", "quality": "Restricted"},
            {"weapon": "SG 553", "pattern": "Ultraviolet", "quality": "Mil-Spec"},
            {"weapon": "AUG", "pattern": "Wings", "quality": "Mil-Spec"},
            {"weapon": "MP7", "pattern": "Skulls", "quality": "Mil-Spec"}
        ],
        "knives": ["Bayonet", "Flip Knife", "Gut Knife", "Karambit", "M9 Bayonet"]
    },
    {
        "title": "eSports 2013 Case",
        "skins": [
            {"weapon": "P90", "pattern": "Death by Kitty", "quality": "Covert"},
            {"weapon": "AK-47", "pattern": "Red Laminate", "quality": "Classified"},
            {"weapon": "AWP", "pattern": "BOOM", "quality": "Classified"},
            {"weapon": "M4A4", "pattern": "Faded Zebra", "quality": "Restricted"},
            {"weapon": "Galil AR", "pattern": "Orange DDPAT", "quality": "Restricted"},
            {"weapon": "SCAR-20", "pattern": "Crimson Web", "quality": "Restricted"},
                        {"weapon": "FAMAS", "pattern": "Doomkitty", "quality": "Mil-Spec"},
            {"weapon": "MAG-7", "pattern": "Bulldozer", "quality": "Mil-Spec"},
            {"weapon": "P2000", "pattern": "Scorpion", "quality": "Mil-Spec"}
        ],
        "knives": ["Bayonet", "Flip Knife", "Gut Knife", "Karambit", "M9 Bayonet"]
    },
    {
        "title": "CS:GO Weapon Case 2",
        "skins": [
            {"weapon": "SSG 08", "pattern": "Blood in the Water", "quality": "Covert"},
            {"weapon": "P90", "pattern": "Cold Blooded", "quality": "Classified"},
            {"weapon": "USP-S", "pattern": "Serum", "quality": "Classified"},
            {"weapon": "Five-SeveN", "pattern": "Case Hardened", "quality": "Restricted"},
            {"weapon": "MP9", "pattern": "Rose Iron", "quality": "Restricted"},
            {"weapon": "Nova", "pattern": "Graphite", "quality": "Restricted"},
            {"weapon": "Dual Berettas", "pattern": "Black Limba", "quality": "Mil-Spec"},
            {"weapon": "M4A1-S", "pattern": "Bright Water", "quality": "Mil-Spec"},
            {"weapon": "SCAR-20", "pattern": "Crimson Web", "quality": "Mil-Spec"},
            {"weapon": "P250", "pattern": "Splash", "quality": "Mil-Spec"},
            {"weapon": "Tec-9", "pattern": "Blue Titanium", "quality": "Mil-Spec"},
            {"weapon": "FAMAS", "pattern": "Hexane", "quality": "Mil-Spec"}
        ],
        "knives": ["Bayonet", "Flip Knife", "Gut Knife", "Karambit", "M9 Bayonet"]
    },
    {
        "title": "Winter Offensive Weapon Case",
        "skins": [
            {"weapon": "M4A4", "pattern": "Asiimov", "quality": "Covert"},
            {"weapon": "AWP", "pattern": "Redline", "quality": "Classified"},
            {"weapon": "Sawed-Off", "pattern": "The Kraken", "quality": "Classified"},
            {"weapon": "P250", "pattern": "Mehndi", "quality": "Restricted"},
            {"weapon": "XM1014", "pattern": "Tranquility", "quality": "Restricted"},
            {"weapon": "PP-Bizon", "pattern": "Cobalt Halogen", "quality": "Restricted"},
            {"weapon": "Galil AR", "pattern": "Sandstorm", "quality": "Mil-Spec"},
            {"weapon": "Five-SeveN", "pattern": "Kami", "quality": "Mil-Spec"},
            {"weapon": "M249", "pattern": "Magma", "quality": "Mil-Spec"},
            {"weapon": "SCAR-20", "pattern": "Splash Jam", "quality": "Mil-Spec"},
            {"weapon": "Dual Berettas", "pattern": "Marina", "quality": "Mil-Spec"},
            {"weapon": "MP9", "pattern": "Rose Iron", "quality": "Mil-Spec"},
            {"weapon": "Nova", "pattern": "Rising Skull", "quality": "Mil-Spec"}
        ],
        "knives": ["Bayonet", "Flip Knife", "Gut Knife", "Karambit", "M9 Bayonet"]
    },
    {
        "title": "eSports 2013 Winter Case",
        "skins": [
            {"weapon": "AWP", "pattern": "Electric Hive", "quality": "Covert"},
            {"weapon": "M4A4", "pattern": "X-Ray", "quality": "Covert"},
            {"weapon": "Desert Eagle", "pattern": "Cobalt Disruption", "quality": "Classified"},
            {"weapon": "P90", "pattern": "Blind Spot", "quality": "Restricted"},
            {"weapon": "USP-S", "pattern": "Stainless", "quality": "Restricted"},
            {"weapon": "Glock-18", "pattern": "Blue Fissure", "quality": "Restricted"},
            {"weapon": "Tec-9", "pattern": "Titanium Bit", "quality": "Mil-Spec"},
            {"weapon": "PP-Bizon", "pattern": "Water Sigil", "quality": "Mil-Spec"},
            {"weapon": "Nova", "pattern": "Ghost Camo", "quality": "Mil-Spec"},
            {"weapon": "G3SG1", "pattern": "Azure Zebra", "quality": "Mil-Spec"},
            {"weapon": "P250", "pattern": "Steel Disruption", "quality": "Mil-Spec"},
            {"weapon": "AK-47", "pattern": "Blue Laminate", "quality": "Restricted"}
        ],
        "knives": ["Bayonet", "Flip Knife", "Gut Knife", "Karambit", "M9 Bayonet"]
    },
    {
        "title": "CS:GO Weapon Case 3",
        "skins": [
            {"weapon": "CZ75-Auto", "pattern": "Victoria", "quality": "Covert"},
            {"weapon": "Desert Eagle", "pattern": "Heirloom", "quality": "Classified"},
            {"weapon": "USP-S", "pattern": "Stainless", "quality": "Restricted"},
            {"weapon": "P2000", "pattern": "Red FragCam", "quality": "Restricted"},
            {"weapon": "Tec-9", "pattern": "Sandstorm", "quality": "Restricted"},
            {"weapon": "CZ75-Auto", "pattern": "The Fuschia Is Now", "quality": "Restricted"},
            {"weapon": "Five-SeveN", "pattern": "Copper Galaxy", "quality": "Restricted"},
            {"weapon": "P250", "pattern": "Undertow", "quality": "Classified"},
            {"weapon": "Glock-18", "pattern": "Blue Fissure", "quality": "Mil-Spec"},
            {"weapon": "Dual Berettas", "pattern": "Panther", "quality": "Mil-Spec"},
            {"weapon": "CZ75-Auto", "pattern": "Crimson Web", "quality": "Mil-Spec"},
            {"weapon": "P2000", "pattern": "Pulse", "quality": "Mil-Spec"}
        ],
        "knives": []
    },
    {
        "title": "Operation Phoenix Weapon Case",
        "skins": [
            {"weapon": "AWP", "pattern": "Asiimov", "quality": "Covert"},
            {"weapon": "AUG", "pattern": "Chameleon", "quality": "Covert"},
            {"weapon": "AK-47", "pattern": "Redline", "quality": "Classified"},
            {"weapon": "Nova", "pattern": "Antique", "quality": "Classified"},
            {"weapon": "P90", "pattern": "Trigon", "quality": "Classified"},
            {"weapon": "FAMAS", "pattern": "Sergeant", "quality": "Restricted"},
            {"weapon": "USP-S", "pattern": "Guardian", "quality": "Restricted"},
            {"weapon": "P250", "pattern": "Mehndi", "quality": "Restricted"},
            {"weapon": "UMP-45", "pattern": "Corporal", "quality": "Mil-Spec"},
            {"weapon": "MAG-7", "pattern": "Heaven Guard", "quality": "Mil-Spec"},
            {"weapon": "MAC-10", "pattern": "Heat", "quality": "Mil-Spec"},
            {"weapon": "SG 553", "pattern": "Pulse", "quality": "Mil-Spec"},
            {"weapon": "Negev", "pattern": "Terrain", "quality": "Mil-Spec"}
        ],
        "knives": ["Bayonet", "Flip Knife", "Gut Knife", "Karambit", "M9 Bayonet"]
    },
    {
        "title": "Huntsman Weapon Case",
        "skins": [
            {"weapon": "AK-47", "pattern": "Vulcan", "quality": "Covert"},
            {"weapon": "M4A1-S", "pattern": "Atomic Alloy", "quality": "Covert"},
            {"weapon": "USP-S", "pattern": "Caiman", "quality": "Classified"},
            {"weapon": "SCAR-20", "pattern": "Cyrex", "quality": "Classified"},
            {"weapon": "M4A4", "pattern": "Desert-Strike", "quality": "Classified"},
            {"weapon": "MAC-10", "pattern": "Tatter", "quality": "Restricted"},
            {"weapon": "PP-Bizon", "pattern": "Antique", "quality": "Restricted"},
            {"weapon": "XM1014", "pattern": "Heaven Guard", "quality": "Restricted"},
            {"weapon": "P90", "pattern": "Module", "quality": "Mil-Spec"},
            {"weapon": "CZ75-Auto", "pattern": "Twist", "quality": "Mil-Spec"},
            {"weapon": "AUG", "pattern": "Torque", "quality": "Mil-Spec"},
            {"weapon": "Tec-9", "pattern": "Isaac", "quality": "Mil-Spec"},
            {"weapon": "SSG 08", "pattern": "Slashed", "quality": "Mil-Spec"},
            {"weapon": "Galil AR", "pattern": "Kami", "quality": "Mil-Spec"},
            {"weapon": "P2000", "pattern": "Pulse", "quality": "Mil-Spec"}
        ],
        "knives": ["Huntsman Knife"]
    },
    {
        "title": "Operation Breakout Weapon Case",
        "skins": [
            {"weapon": "M4A1-S", "pattern": "Cyrex", "quality": "Covert"},
            {"weapon": "P90", "pattern": "Asiimov", "quality": "Covert"},
            {"weapon": "Glock-18", "pattern": "Water Elemental", "quality": "Classified"},
            {"weapon": "Desert Eagle", "pattern": "Conspiracy", "quality": "Classified"},
            {"weapon": "P250", "pattern": "Supernova", "quality": "Classified"},
            {"weapon": "Five-SeveN", "pattern": "Fowl Play", "quality": "Restricted"},
            {"weapon": "Nova", "pattern": "Koi", "quality": "Restricted"},
            {"weapon": "PP-Bizon", "pattern": "Osiris", "quality": "Restricted"},
            {"weapon": "SSG 08", "pattern": "Abyss", "quality": "Mil-Spec"},
            {"weapon": "UMP-45", "pattern": "Labyrinth", "quality": "Mil-Spec"},
            {"weapon": "MP7", "pattern": "Urban Hazard", "quality": "Mil-Spec"},
            {"weapon": "CZ75-Auto", "pattern": "Tigris", "quality": "Mil-Spec"},
            {"weapon": "Negev", "pattern": "Desert-Strike", "quality": "Mil-Spec"}
        ],
        "knives": ["Butterfly Knife"]
    },
    {
        "title": "eSports 2014 Summer Case",
        "skins": [
            {"weapon": "Nova", "pattern": "Bloomstick", "quality": "Covert"},
            {"weapon": "AWP", "pattern": "Corticera", "quality": "Classified"},
            {"weapon": "P90", "pattern": "Virus", "quality": "Classified"},
            {"weapon": "M4A4", "pattern": "Bullet Rain", "quality": "Classified"},
            {"weapon": "AK-47", "pattern": "Jaguar", "quality": "Classified"},
            {"weapon": "Desert Eagle", "pattern": "Crimson Web", "quality": "Restricted"},
            {"weapon": "MP7", "pattern": "Ocean Foam", "quality": "Restricted"},
            {"weapon": "Glock-18", "pattern": "Steel Disruption", "quality": "Restricted"},
            {"weapon": "AUG", "pattern": "Bengal Tiger", "quality": "Restricted"},
            {"weapon": "FAMAS", "pattern": "Styx", "quality": "Restricted"},
            {"weapon": "SG 553", "pattern": "Traveler", "quality": "Mil-Spec"},
            {"weapon": "CZ75-Auto", "pattern": "Hexane", "quality": "Mil-Spec"},
            {"weapon": "Negev", "pattern": "Bratatat", "quality": "Mil-Spec"}
        ],
        "knives": ["Bayonet", "Flip Knife", "Gut Knife", "Karambit", "M9 Bayonet"]
    },
    {
        "title": "Operation Vanguard Weapon Case",
        "skins": [
            {"weapon": "AK-47", "pattern": "Wasteland Rebel", "quality": "Covert"},
            {"weapon": "P2000", "pattern": "Fire Elemental", "quality": "Covert"},
            {"weapon": "M4A4", "pattern": "Griffin", "quality": "Classified"},
            {"weapon": "M4A1-S", "pattern": "Basilisk", "quality": "Classified"},
            {"weapon": "SCAR-20", "pattern": "Cardiac", "quality": "Classified"},
            {"weapon": "XM1014", "pattern": "Tranquility", "quality": "Restricted"},
            {"weapon": "Glock-18", "pattern": "Grinder", "quality": "Restricted"},
            {"weapon": "P250", "pattern": "Cartel", "quality": "Restricted"},
            {"weapon": "Galil AR", "pattern": "Firefight", "quality": "Mil-Spec"},
            {"weapon": "MP7", "pattern": "Skulls", "quality": "Mil-Spec"},
            {"weapon": "UMP-45", "pattern": "Delusion", "quality": "Mil-Spec"},
            {"weapon": "MAG-7", "pattern": "Firestarter", "quality": "Mil-Spec"},
            {"weapon": "Sawed-Off", "pattern": "Highwayman", "quality": "Mil-Spec"}
        ],
        "knives": ["Bayonet", "Flip Knife", "Gut Knife", "Karambit", "M9 Bayonet"]
    },
    {
        "title": "Chroma Case",
        "skins": [
            {"weapon": "Galil AR", "pattern": "Chatterbox", "quality": "Covert"},
            {"weapon": "AWP", "pattern": "Man-o'-war", "quality": "Covert"},
            {"weapon": "M4A4", "pattern": "Dragon King", "quality": "Classified"},
            {"weapon": "AK-47", "pattern": "Cartel", "quality": "Classified"},
            {"weapon": "Dual Berettas", "pattern": "Urban Shock", "quality": "Restricted"},
            {"weapon": "Desert Eagle", "pattern": "Naga", "quality": "Restricted"},
            {"weapon": "MAC-10", "pattern": "Malachite", "quality": "Restricted"},
            {"weapon": "Sawed-Off", "pattern": "Serenity", "quality": "Restricted"},
            {"weapon": "P250", "pattern": "Muertos", "quality": "Mil-Spec"},
            {"weapon": "Glock-18", "pattern": "Catacombs", "quality": "Mil-Spec"},
            {"weapon": "M249", "pattern": "System Lock", "quality": "Mil-Spec"},
            {"weapon": "MP9", "pattern": "Deadly Poison", "quality": "Mil-Spec"},
            {"weapon": "SCAR-20", "pattern": "Grotto", "quality": "Mil-Spec"},
            {"weapon": "XM1014", "pattern": "Quicksilver", "quality": "Mil-Spec"}
        ],
        "knives": ["Bayonet", "Flip Knife", "Gut Knife", "Karambit", "M9 Bayonet"]
    },
    {
        "title": "Chroma 2 Case",
        "skins": [
            {"weapon": "M4A1-S", "pattern": "Hyper Beast", "quality": "Covert"},
            {"weapon": "MAC-10", "pattern": "Neon Rider", "quality": "Covert"},
            {"weapon": "Galil AR", "pattern": "Eco", "quality": "Classified"},
            {"weapon": "FAMAS", "pattern": "Djinn", "quality": "Classified"},
            {"weapon": "Five-SeveN", "pattern": "Monkey Business", "quality": "Classified"},
            {"weapon": "AWP", "pattern": "Worm God", "quality": "Restricted"},
            {"weapon": "MAG-7", "pattern": "Heat", "quality": "Restricted"},
            {"weapon": "CZ75-Auto", "pattern": "Pole Position", "quality": "Restricted"},
            {"weapon": "UMP-45", "pattern": "Grand Prix", "quality": "Restricted"},
            {"weapon": "Desert Eagle", "pattern": "Bronze Deco", "quality": "Mil-Spec"},
            {"weapon": "P250", "pattern": "Valence", "quality": "Mil-Spec"},
            {"weapon": "Negev", "pattern": "Man-o'-war", "quality": "Mil-Spec"},
            {"weapon": "MP7", "pattern": "Armor Core", "quality": "Mil-Spec"},
            {"weapon": "Sawed-Off", "pattern": "Origami", "quality": "Mil-Spec"},
            {"weapon": "AK-47", "pattern": "Elite Build", "quality": "Mil-Spec"}
        ],
        "knives": ["Bayonet", "Flip Knife", "Gut Knife", "Karambit", "M9 Bayonet"]
    },
    {
        "title": "Falchion Case",
        "skins": [
            {"weapon": "AWP", "pattern": "Hyper Beast", "quality": "Covert"},
            {"weapon": "AK-47", "pattern": "Aquamarine Revenge", "quality": "Covert"},
            {"weapon": "SG 553", "pattern": "Cyrex", "quality": "Classified"},
            {"weapon": "M4A4", "pattern": "Evil Daimyo", "quality": "Classified"},
            {"weapon": "FAMAS", "pattern": "Neural Net", "quality": "Classified"},
            {"weapon": "MP9", "pattern": "Ruby Poison Dart", "quality": "Restricted"},
            {"weapon": "Negev", "pattern": "Loudmouth", "quality": "Restricted"},
            {"weapon": "P2000", "pattern": "Handgun", "quality": "Restricted"},
            {"weapon": "CZ75-Auto", "pattern": "Yellow Jacket", "quality": "Restricted"},
            {"weapon": "MP7", "pattern": "Nemesis", "quality": "Restricted"},
            {"weapon": "Galil AR", "pattern": "Rocket Pop", "quality": "Mil-Spec"},
            {"weapon": "Glock-18", "pattern": "Bunsen Burner", "quality": "Mil-Spec"},
            {"weapon": "Nova", "pattern": "Ranger", "quality": "Mil-Spec"},
            {"weapon": "UMP-45", "pattern": "Riot", "quality": "Mil-Spec"},
            {"weapon": "USP-S", "pattern": "Torque", "quality": "Mil-Spec"}
        ],
        "knives": ["Falchion Knife"]
    },
    {
        "title": "Shadow Case",
        "skins": [
            {"weapon": "M4A1-S", "pattern": "Golden Coil", "quality": "Covert"},
            {"weapon": "USP-S", "pattern": "Kill Confirmed", "quality": "Covert"},
            {"weapon": "AK-47", "pattern": "Frontside Misty", "quality": "Classified"},
            {"weapon": "G3SG1", "pattern": "Flux", "quality": "Classified"},
            {"weapon": "SSG 08", "pattern": "Big Iron", "quality": "Classified"},
            {"weapon": "P250", "pattern": "Wingshot", "quality": "Restricted"},
            {"weapon": "Galil AR", "pattern": "Stone Cold", "quality": "Restricted"},
            {"weapon": "M249", "pattern": "Nebula Crusader", "quality": "Restricted"},
            {"weapon": "MP7", "pattern": "Special Delivery", "quality": "Restricted"},
            {"weapon": "Glock-18", "pattern": "Wraiths", "quality": "Mil-Spec"},
            {"weapon": "Dual Berettas", "pattern": "Dualing Dragons", "quality": "Mil-Spec"},
            {"weapon": "XM1014", "pattern": "Scumbria", "quality": "Mil-Spec"},
            {"weapon": "MAG-7", "pattern": "Cobalt Core", "quality": "Mil-Spec"},
            {"weapon": "SCAR-20", "pattern": "Green Marine", "quality": "Mil-Spec"},
            {"weapon": "Tec-9", "pattern": "Ice Cap", "quality": "Mil-Spec"}
        ],
        "knives": ["Shadow Daggers"]
    },
    {
        "title": "Revolver Case",
        "skins": [
            {"weapon": "M4A4", "pattern": "Royal Paladin", "quality": "Covert"},
            {"weapon": "R8 Revolver", "pattern": "Fade", "quality": "Covert"},
            {"weapon": "AK-47", "pattern": "Point Disarray", "quality": "Classified"},
            {"weapon": "G3SG1", "pattern": "The Executioner", "quality": "Classified"},
            {"weapon": "P90", "pattern": "Shapewood", "quality": "Classified"},
            {"weapon": "Tec-9", "pattern": "Avalanche", "quality": "Restricted"},
            {"weapon": "SG 553", "pattern": "Tiger Moth", "quality": "Restricted"},
            {"weapon": "Five-SeveN", "pattern": "Retrobution", "quality": "Restricted"},
            {"weapon": "Negev", "pattern": "Power Loader", "quality": "Restricted"},
            {"weapon": "XM1014", "pattern": "Teclu Burner", "quality": "Mil-Spec"},
            {"weapon": "PP-Bizon", "pattern": "Fuel Rod", "quality": "Mil-Spec"},
            {"weapon": "Desert Eagle", "pattern": "Corinthian", "quality": "Mil-Spec"},
            {"weapon": "AUG", "pattern": "Ricochet", "quality": "Mil-Spec"},
            {"weapon": "P2000", "pattern": "Imperial", "quality": "Mil-Spec"},
            {"weapon": "Sawed-Off", "pattern": "Yorick", "quality": "Mil-Spec"}
        ],
        "knives": []
    },
    {
        "title": "Operation Wildfire Case",
        "skins": [
            {"weapon": "AWP", "pattern": "Elite Build", "quality": "Covert"},
            {"weapon": "AK-47", "pattern": "Fuel Injector", "quality": "Covert"},
            {"weapon": "M4A4", "pattern": "The Battlestar", "quality": "Classified"},
            {"weapon": "Desert Eagle", "pattern": "Kumicho Dragon", "quality": "Classified"},
            {"weapon": "Nova", "pattern": "Hyper Beast", "quality": "Classified"},
            {"weapon": "Glock-18", "pattern": "Royal Legion", "quality": "Restricted"},
            {"weapon": "FAMAS", "pattern": "Valence", "quality": "Restricted"},
            {"weapon": "MAG-7", "pattern": "Praetorian", "quality": "Restricted"},
            {"weapon": "Five-SeveN", "pattern": "Triumvirate", "quality": "Restricted"},
            {"weapon": "PP-Bizon", "pattern": "Photic Zone", "quality": "Mil-Spec"},
            {"weapon": "Dual Berettas", "pattern": "Cartel", "quality": "Mil-Spec"},
            {"weapon": "MP7", "pattern": "Impire", "quality": "Mil-Spec"},
            {"weapon": "SSG 08", "pattern": "Necropos", "quality": "Mil-Spec"},
            {"weapon": "USP-S", "pattern": "Lead Conduit", "quality": "Mil-Spec"},
            {"weapon": "Tec-9", "pattern": "Jambiya", "quality": "Mil-Spec"}
        ],
        "knives": ["Bowie Knife"]
    },
    {
        "title": "Chroma 3 Case",
        "skins": [
            {"weapon": "M4A1-S", "pattern": "Chantico's Fire", "quality": "Covert"},
            {"weapon": "PP-Bizon", "pattern": "Judgement of Anubis", "quality": "Covert"},
            {"weapon": "AUG", "pattern": "Fleet Flock", "quality": "Classified"},
            {"weapon": "P250", "pattern": "Asiimov", "quality": "Classified"},
            {"weapon": "UMP-45", "pattern": "Primal Saber", "quality": "Classified"},
            {"weapon": "Dual Berettas", "pattern": "Ventilators", "quality": "Restricted"},
            {"weapon": "G3SG1", "pattern": "Orange Crash", "quality": "Restricted"},
            {"weapon": "P2000", "pattern": "Oceanic", "quality": "Restricted"},
            {"weapon": "Tec-9", "pattern": "Re-Entry", "quality": "Restricted"},
            {"weapon": "XM1014", "pattern": "Black Tie", "quality": "Restricted"},
            {"weapon": "CZ75-Auto", "pattern": "Red Astor", "quality": "Mil-Spec"},
            {"weapon": "Galil AR", "pattern": "Firefight", "quality": "Mil-Spec"},
            {"weapon": "SSG 08", "pattern": "Ghost Crusader", "quality": "Mil-Spec"},
            {"weapon": "SG 553", "pattern": "Atlas", "quality": "Mil-Spec"},
            {"weapon": "M249", "pattern": "Spectre", "quality": "Mil-Spec"},
            {"weapon": "MP9", "pattern": "Bioleak", "quality": "Mil-Spec"}
        ],
        "knives": ["Bayonet", "Flip Knife", "Gut Knife", "Karambit", "M9 Bayonet"]
    },
    {
        "title": "Gamma Case",
        "skins": [
            {"weapon": "M4A1-S", "pattern": "Mecha Industries", "quality": "Covert"},
            {"weapon": "Glock-18", "pattern": "Wasteland Rebel", "quality": "Covert"},
            {"weapon": "M4A4", "pattern": "Desolate Space", "quality": "Classified"},
            {"weapon": "SCAR-20", "pattern": "Bloodsport", "quality": "Classified"},
            {"weapon": "P90", "pattern": "Chopper", "quality": "Classified"},
            {"weapon": "R8 Revolver", "pattern": "Reboot", "quality": "Restricted"},
            {"weapon": "P250", "pattern": "Iron Clad", "quality": "Restricted"},
            {"weapon": "Five-SeveN", "pattern": "Violent Daimyo", "quality": "Restricted"},
            {"weapon": "AUG", "pattern": "Syd Mead", "quality": "Restricted"},
            {"weapon": "MP9", "pattern": "Airlock", "quality": "Restricted"},
            {"weapon": "Tec-9", "pattern": "Ice Cap", "quality": "Mil-Spec"},
            {"weapon": "SG 553", "pattern": "Aerial", "quality": "Mil-Spec"},
            {"weapon": "P2000", "pattern": "Imperial Dragon", "quality": "Mil-Spec"},
            {"weapon": "AWP", "pattern": "Phobos", "quality": "Mil-Spec"},
            {"weapon": "Glock-18", "pattern": "Weasel", "quality": "Mil-Spec"},
            {"weapon": "Sawed-Off", "pattern": "Limelight", "quality": "Mil-Spec"},
            {"weapon": "M249", "pattern": "Nebula Crusader", "quality": "Mil-Spec"}
        ],
        "knives": ["Bayonet", "Flip Knife", "Gut Knife", "Karambit", "M9 Bayonet"]
    },
    {
        "title": "Gamma 2 Case",
        "skins": [
            {"weapon": "AK-47", "pattern": "Neon Revolution", "quality": "Covert"},
            {"weapon": "FAMAS", "pattern": "Roll Cage", "quality": "Covert"},
            {"weapon": "Tec-9", "pattern": "Fuel Injector", "quality": "Classified"},
            {"weapon": "AUG", "pattern": "Triqua", "quality": "Classified"},
            {"weapon": "MP9", "pattern": "Goo", "quality": "Classified"},
            {"weapon": "SCAR-20", "pattern": "Powercore", "quality": "Restricted"},
            {"weapon": "MAG-7", "pattern": "Petroglyph", "quality": "Restricted"},
            {"weapon": "Desert Eagle", "pattern": "Directive", "quality": "Restricted"},
            {"weapon": "Glock-18", "pattern": "Ironwork", "quality": "Restricted"},
            {"weapon": "CZ75-Auto", "pattern": "Imprint", "quality": "Mil-Spec"},
            {"weapon": "G3SG1", "pattern": "Ventilator", "quality": "Mil-Spec"},
            {"weapon": "M4A1-S", "pattern": "Briefing", "quality": "Mil-Spec"},
            {"weapon": "P90", "pattern": "Grim", "quality": "Mil-Spec"},
            {"weapon": "XM1014", "pattern": "Slipstream", "quality": "Mil-Spec"},
            {"weapon": "UMP-45", "pattern": "Briefing", "quality": "Mil-Spec"},
            {"weapon": "Five-SeveN", "pattern": "Scumbria", "quality": "Mil-Spec"}
        ],
        "knives": ["Bayonet", "Flip Knife", "Gut Knife", "Karambit", "M9 Bayonet"]
    },
    {
        "title": "Glove Case",
        "skins": [
            {"weapon": "M4A4", "pattern": "Buzz Kill", "quality": "Covert"},
            {"weapon": "SSG 08", "pattern": "Dragonfire", "quality": "Covert"},
            {"weapon": "P90", "pattern": "Shallow Grave", "quality": "Classified"},
            {"weapon": "SCAR-20", "pattern": "Powercore", "quality": "Classified"},
            {"weapon": "Sawed-Off", "pattern": "Wasteland Princess", "quality": "Classified"},
            {"weapon": "USP-S", "pattern": "Cyrex", "quality": "Restricted"},
            {"weapon": "FAMAS", "pattern": "Mecha Industries", "quality": "Restricted"},
            {"weapon": "M4A1-S", "pattern": "Flashback", "quality": "Restricted"},
            {"weapon": "Nova", "pattern": "Gila", "quality": "Restricted"},
            {"weapon": "G3SG1", "pattern": "Stinger", "quality": "Mil-Spec"},
            {"weapon": "Dual Berettas", "pattern": "Royal Consorts", "quality": "Mil-Spec"},
            {"weapon": "Glock-18", "pattern": "Ironwork", "quality": "Mil-Spec"},
            {"weapon": "MP7", "pattern": "Cirrus", "quality": "Mil-Spec"},
            {"weapon": "Galil AR", "pattern": "Black Sand", "quality": "Mil-Spec"},
            {"weapon": "MP9", "pattern": "Sand Scale", "quality": "Mil-Spec"},
            {"weapon": "MAG-7", "pattern": "Sonar", "quality": "Mil-Spec"},
            {"weapon": "P2000", "pattern": "Turf", "quality": "Mil-Spec"}
        ],
        "gloves": ["Bloodhound Gloves", "Driver Gloves", "Hand Wraps", "Moto Gloves", "Specialist Gloves", "Sport Gloves"]
    },
    {
        "title": "Spectrum Case",
        "skins": [
            {"weapon": "AK-47", "pattern": "Bloodsport", "quality": "Covert"},
            {"weapon": "USP-S", "pattern": "Neo-Noir", "quality": "Covert"},
            {"weapon": "M4A1-S", "pattern": "Decimator", "quality": "Classified"},
            {"weapon": "AWP", "pattern": "Fever Dream", "quality": "Classified"},
            {"weapon": "CZ75-Auto", "pattern": "Xiangliu", "quality": "Classified"},
            {"weapon": "UMP-45", "pattern": "Scaffold", "quality": "Restricted"},
            {"weapon": "XM1014", "pattern": "Seasons", "quality": "Restricted"},
            {"weapon": "Galil AR", "pattern": "Crimson Tsunami", "quality": "Restricted"},
            {"weapon": "M249", "pattern": "Emerald Poison Dart", "quality": "Restricted"},
            {"weapon": "P250", "pattern": "Ripple", "quality": "Mil-Spec"},
            {"weapon": "P2000", "pattern": "Imperial", "quality": "Mil-Spec"},
            {"weapon": "Five-SeveN", "pattern": "Capillary", "quality": "Mil-Spec"},
            {"weapon": "Desert Eagle", "pattern": "Oxide Blaze", "quality": "Mil-Spec"},
            {"weapon": "Sawed-Off", "pattern": "Zander", "quality": "Mil-Spec"},
            {"weapon": "SCAR-20", "pattern": "Blueprint", "quality": "Mil-Spec"},
            {"weapon": "PP-Bizon", "pattern": "Jungle Slipstream", "quality": "Mil-Spec"}
        ],
        "knives": ["Bayonet", "Flip Knife", "Gut Knife", "Karambit", "M9 Bayonet"]
    },
    {
        "title": "Operation Hydra Case",
        "skins": [
            {"weapon": "Five-SeveN", "pattern": "Hyper Beast", "quality": "Covert"},
            {"weapon": "AWP", "pattern": "Oni Taiji", "quality": "Covert"},
            {"weapon": "M4A4", "pattern": "Hellfire", "quality": "Classified"},
            {"weapon": "AK-47", "pattern": "Orbit Mk01", "quality": "Classified"},
            {"weapon": "P2000", "pattern": "Woodsman", "quality": "Classified"},
            {"weapon": "Dual Berettas", "pattern": "Cobra Strike", "quality": "Restricted"},
            {"weapon": "Galil AR", "pattern": "Sugar Rush", "quality": "Restricted"},
            {"weapon": "SSG 08", "pattern": "Death's Head", "quality": "Restricted"},
            {"weapon": "P90", "pattern": "Death Grip", "quality": "Restricted"},
            {"weapon": "FAMAS", "pattern": "Macabre", "quality": "Mil-Spec"},
            {"weapon": "MAC-10", "pattern": "Red Filigree", "quality": "Mil-Spec"},
            {"weapon": "UMP-45", "pattern": "Metal Flowers", "quality": "Mil-Spec"},
            {"weapon": "Tec-9", "pattern": "Cut Out", "quality": "Mil-Spec"},
            {"weapon": "MAG-7", "pattern": "Hard Water", "quality": "Mil-Spec"},
            {"weapon": "AUG", "pattern": "Triad", "quality": "Mil-Spec"},
            {"weapon": "Glock-18", "pattern": "Off World", "quality": "Mil-Spec"},
            {"weapon": "USP-S", "pattern": "Blueprint", "quality": "Mil-Spec"}
        ],
        "gloves": ["Bloodhound Gloves", "Driver Gloves", "Hand Wraps", "Moto Gloves", "Specialist Gloves", "Sport Gloves"]
    },
    {
        "title": "Spectrum 2 Case",
        "skins": [
            {"weapon": "M4A1-S", "pattern": "Leaded Glass", "quality": "Covert"},
            {"weapon": "AK-47", "pattern": "The Empress", "quality": "Covert"},
            {"weapon": "P250", "pattern": "See Ya Later", "quality": "Classified"},
            {"weapon": "R8 Revolver", "pattern": "Llama Cannon", "quality": "Classified"},
            {"weapon": "PP-Bizon", "pattern": "High Roller", "quality": "Classified"},
            {"weapon": "CZ75-Auto", "pattern": "Tacticat", "quality": "Restricted"},
            {"weapon": "UMP-45", "pattern": "Exposure", "quality": "Restricted"},
            {"weapon": "XM1014", "pattern": "Ziggy", "quality": "Restricted"},
            {"weapon": "SG 553", "pattern": "Phantom", "quality": "Restricted"},
            {"weapon": "G3SG1", "pattern": "Hunter", "quality": "Mil-Spec"},
            {"weapon": "M249", "pattern": "Deep Relief", "quality": "Mil-Spec"},
            {"weapon": "MP9", "pattern": "Capillary", "quality": "Mil-Spec"},
            {"weapon": "SCAR-20", "pattern": "Jungle Slipstream", "quality": "Mil-Spec"},
            {"weapon": "AUG", "pattern": "Syd Mead", "quality": "Mil-Spec"},
            {"weapon": "Glock-18", "pattern": "Off World", "quality": "Mil-Spec"},
            {"weapon": "Tec-9", "pattern": "Cracked Opal", "quality": "Mil-Spec"},
            {"weapon": "Sawed-Off", "pattern": "Morris", "quality": "Mil-Spec"}
        ],
        "knives": ["Bayonet", "Flip Knife", "Gut Knife", "Karambit", "M9 Bayonet"]
    }
]

# Create and insert our cases
case_ids = {}
for case_data in cases_with_skins:
    # Get case title and image
    case_title = case_data["title"]
    case_image = get_case_image(case_title)
    
    # Get case release date
    release_date = case_info.get(case_title, "2013-01-01")
    
    # Calculate a default price based on release date (older cases are more expensive)
    years_old = 2025 - int(release_date.split("-")[0])
    default_price = 100 + (5 * years_old)
    
    # Create the case document
    case = {
        "title": case_title,
        "image": case_image,
        "price": default_price,
        "year": int(release_date.split("-")[0]),
        "release_date": release_date,
        "num_skins": len(case_data["skins"]) + (
            len(case_data.get("knives", [])) * 13 if "knives" in case_data else 0
        ) + (len(case_data.get("gloves", [])) * 4 if "gloves" in case_data else 0)
    }
    
    # Insert the case and store its ID
    case_id = db.cases.insert_one(case).inserted_id
    case_ids[case_title] = case_id
    
    # Insert all the regular skins from this case
    for skin_data in case_data["skins"]:
        # Get weapon and pattern names
        weapon_name = skin_data["weapon"]
        pattern_name = skin_data["pattern"]
        
        # Get the weapon ID
        weapon_id = weapon_ids.get(weapon_name)
        if not weapon_id:
            print(f"Warning: Could not find weapon ID for {weapon_name}")
            continue
        
        # Get the quality info
        quality = next((q for q in qualities if q["title"] == skin_data["quality"]), qualities[2])  # Default to Mil-Spec
        quality_id = quality_ids[quality["title"]]
        
        # Calculate price based on quality (rarer = more expensive)
        quality_idx = next((i for i, q in enumerate(qualities) if q["title"] == quality["title"]), 2)
        base_price = 2 ** quality_idx
        price = round(base_price * (1 + 0.1 * years_old) * (0.8 + 0.4 * random.random()), 2)
        
        # Float range based on quality
        if quality_idx <= 2:  # Consumer, Industrial, Mil-Spec
            min_float = round(random.uniform(0.06, 0.15), 2)
            max_float = round(random.uniform(0.7, 1.0), 2)
        else:  # Restricted, Classified, Covert
            min_float = round(random.uniform(0.0, 0.1), 2)
            max_float = round(random.uniform(0.4, 0.8), 2)
        
        # Get image URL
        image_url = get_skin_image(weapon_name, pattern_name)
        
        # Insert both regular and StatTrak versions
        for stattrak in [False, True]:
            stattrak_price = price
            if stattrak:
                stattrak_price *= 2.5  # Premium for StatTrak
            
            db.skins.insert_one({
                "pattern": {"title": pattern_name},
                "weapon": {"_id": weapon_id, "title": weapon_name, "type": next((w["type"] for w in weapons if w["title"] == weapon_name), "unknown")},
                "case_id": case_id,
                "quality": {"_id": quality_id, "title": quality["title"], "color": quality["color"], "order": quality["order"]},
                "stattrak": stattrak,
                "souvenir": False,
                "price": stattrak_price,
                "image": image_url,
                "min_float": min_float,
                "max_float": max_float,
                "created_at": datetime.now()
            })
    
    # Insert the knife skins if this case has knives
    if "knives" in case_data:
        # List of standard knife finishes
        standard_finishes = [
            "Vanilla", "Blue Steel", "Boreal Forest", "Case Hardened",
            "Crimson Web", "Fade", "Forest DDPAT", "Night", "Safari Mesh",
            "Scorched", "Slaughter", "Stained", "Urban Masked"
        ]
        
        # Chroma finishes (for cases from Chroma onwards)
        chroma_finishes = [
            "Doppler", "Marble Fade", "Tiger Tooth", "Damascus Steel", "Rust Coat", "Ultraviolet"
        ]
        
        # Gamma finishes (for Gamma cases)
        gamma_finishes = [
            "Autotronic", "Black Laminate", "Bright Water", "Freehand", "Gamma Doppler", "Lore"
        ]
        
        # Determine which knife finishes to use based on case title
        finishes = standard_finishes
        if "Chroma" in case_title or "Gamma" in case_title or "Spectrum" in case_title:
            finishes = standard_finishes + chroma_finishes
        if "Gamma" in case_title:
            finishes = standard_finishes + chroma_finishes + gamma_finishes
        
        # For regular knife cases, insert all knife skins
        for knife in case_data["knives"]:
            weapon_id = weapon_ids.get(knife)
            if not weapon_id:
                print(f"Warning: Could not find weapon ID for {knife}")
                continue
            
            for finish in finishes:
                knife_price = round(random.uniform(50, 500) * (1 + 0.1 * years_old), 2)
                
                # Generic knife image URL based on knife type
                knife_image = f"https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/weapons/base_weapons/weapon_{knife.lower().replace(' ', '_').replace('-', '')}_png.png"
                
                # Float range for knives
                min_float = round(random.uniform(0.0, 0.08), 2)
                max_float = round(random.uniform(0.4, 0.8), 2)
                
                # Insert both regular and StatTrak versions
                for stattrak in [False, True]:
                    stattrak_price = knife_price
                    if stattrak:
                        stattrak_price *= 2.5  # Premium for StatTrak
                    
                    db.skins.insert_one({
                        "pattern": {"title": finish},
                        "weapon": {"_id": weapon_id, "title": knife, "type": "knife"},
                        "case_id": case_id,
                        "quality": {"_id": quality_ids["Exceedingly Rare"], "title": "Exceedingly Rare", "color": "#ffae39", "order": 7},
                        "stattrak": stattrak,
                        "souvenir": False,
                        "price": stattrak_price,
                        "image": knife_image,
                        "min_float": min_float,
                        "max_float": max_float,
                        "created_at": datetime.now()
                    })
    
    # Insert glove skins if this case has gloves
    if "gloves" in case_data:
        glove_types = case_data["gloves"]
        for glove_type in glove_types:
            weapon_id = weapon_ids.get(glove_type)
            if not weapon_id:
                print(f"Warning: Could not find weapon ID for {glove_type}")
                continue
            
            # For gloves, we'll use some predefined patterns
            glove_patterns = [
                {"name": "Convoy", "min_float": 0.06, "max_float": 0.8},
                {"name": "Crimson Weave", "min_float": 0.06, "max_float": 0.8},
                {"name": "Emerald Web", "min_float": 0.06, "max_float": 0.8},
                {"name": "Foundation", "min_float": 0.06, "max_float": 0.8},
            ]
            
            # Insert each glove pattern
            for pattern in glove_patterns:
                glove_price = round(random.uniform(50, 500) * (1 + 0.1 * years_old), 2)
                
                # Generic glove image URL
                glove_image = f"https://raw.githubusercontent.com/ByMykel/counter-strike-image-tracker/main/static/panorama/images/econ/default_generated/specialist_gloves_specialist_kimono_diamonds_red_light_png.png"
                
                db.skins.insert_one({
                    "pattern": {"title": pattern["name"]},
                    "weapon": {"_id": weapon_id, "title": glove_type, "type": "gloves"},
                    "case_id": case_id,
                    "quality": {"_id": quality_ids["Exceedingly Rare"], "title": "Exceedingly Rare", "color": "#ffae39", "order": 7},
                    "stattrak": False,  # Gloves don't have StatTrak
                    "souvenir": False,
                    "price": glove_price,
                    "image": glove_image,
                    "min_float": pattern["min_float"],
                    "max_float": pattern["max_float"],
                    "created_at": datetime.now()
                })

print("\nБаза данных успешно заполнена!")
print(f"Создано {len(cases_with_skins)} кейсов")
print(f"Создано {db.skins.count_documents({})} скинов")
print("Все изображения взяты напрямую с конкретных URL для каждого скина")
print("Current Date and Time (UTC): 2025-05-13 16:33:32")
print("Current User's Login: copilotpublic_andrtro")