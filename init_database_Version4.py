from pymongo import MongoClient
import uuid

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['csreforge']

# Clear existing collections to avoid duplicates
db.cases.drop()
db.items.drop()
db.users.drop()

# Define rarity levels
rarities = {
    "consumer": {"name": "Consumer Grade", "color": "#b0c3d9"},
    "industrial": {"name": "Industrial Grade", "color": "#5e98d9"},
    "mil_spec": {"name": "Mil-Spec", "color": "#4b69ff"},
    "restricted": {"name": "Restricted", "color": "#8847ff"},
    "classified": {"name": "Classified", "color": "#d32ce6"},
    "covert": {"name": "Covert", "color": "#eb4b4b"},
    "rare_special": {"name": "Rare Special", "color": "#ffae39"}
}

# Define weapon skins
weapons = [
    # First Cases
    # CS:GO Weapon Case
    {"id": str(uuid.uuid4()), "name": "AWP | Lightning Strike", "image": "images/skins/awp_lightning_strike.png", "rarity": "covert", "case_id": "csgo_case_1"},
    {"id": str(uuid.uuid4()), "name": "AK-47 | Case Hardened", "image": "images/skins/ak47_case_hardened.png", "rarity": "classified", "case_id": "csgo_case_1"},
    {"id": str(uuid.uuid4()), "name": "Desert Eagle | Hypnotic", "image": "images/skins/deagle_hypnotic.png", "rarity": "classified", "case_id": "csgo_case_1"},
    {"id": str(uuid.uuid4()), "name": "Glock-18 | Dragon Tattoo", "image": "images/skins/glock_dragon_tattoo.png", "rarity": "restricted", "case_id": "csgo_case_1"},
    {"id": str(uuid.uuid4()), "name": "M4A1-S | Dark Water", "image": "images/skins/m4a1s_dark_water.png", "rarity": "restricted", "case_id": "csgo_case_1"},
    {"id": str(uuid.uuid4()), "name": "USP-S | Dark Water", "image": "images/skins/usps_dark_water.png", "rarity": "restricted", "case_id": "csgo_case_1"},
    {"id": str(uuid.uuid4()), "name": "SG 553 | Ultraviolet", "image": "images/skins/sg553_ultraviolet.png", "rarity": "mil_spec", "case_id": "csgo_case_1"},
    {"id": str(uuid.uuid4()), "name": "Knife | Vanilla", "image": "images/skins/knife_vanilla.png", "rarity": "rare_special", "case_id": "csgo_case_1"},
    
    # CS:GO Weapon Case 2
    {"id": str(uuid.uuid4()), "name": "SSG 08 | Blood in the Water", "image": "images/skins/ssg08_blood_in_the_water.png", "rarity": "covert", "case_id": "csgo_case_2"},
    {"id": str(uuid.uuid4()), "name": "P90 | Cold Blooded", "image": "images/skins/p90_cold_blooded.png", "rarity": "classified", "case_id": "csgo_case_2"},
    {"id": str(uuid.uuid4()), "name": "USP-S | Serum", "image": "images/skins/usps_serum.png", "rarity": "classified", "case_id": "csgo_case_2"},
    {"id": str(uuid.uuid4()), "name": "MP9 | Hypnotic", "image": "images/skins/mp9_hypnotic.png", "rarity": "restricted", "case_id": "csgo_case_2"},
    {"id": str(uuid.uuid4()), "name": "FAMAS | Hexane", "image": "images/skins/famas_hexane.png", "rarity": "mil_spec", "case_id": "csgo_case_2"},
    {"id": str(uuid.uuid4()), "name": "Flip Knife | Vanilla", "image": "images/skins/flip_knife_vanilla.png", "rarity": "rare_special", "case_id": "csgo_case_2"},
    
    # eSports 2013 Case
    {"id": str(uuid.uuid4()), "name": "P90 | Death by Kitty", "image": "images/skins/p90_death_by_kitty.png", "rarity": "covert", "case_id": "esports_2013"},
    {"id": str(uuid.uuid4()), "name": "AWP | BOOM", "image": "images/skins/awp_boom.png", "rarity": "classified", "case_id": "esports_2013"},
    {"id": str(uuid.uuid4()), "name": "AK-47 | Red Laminate", "image": "images/skins/ak47_red_laminate.png", "rarity": "classified", "case_id": "esports_2013"},
    {"id": str(uuid.uuid4()), "name": "Galil AR | Orange DDPAT", "image": "images/skins/galil_orange_ddpat.png", "rarity": "restricted", "case_id": "esports_2013"},
    {"id": str(uuid.uuid4()), "name": "M4A4 | Faded Zebra", "image": "images/skins/m4a4_faded_zebra.png", "rarity": "mil_spec", "case_id": "esports_2013"},
    {"id": str(uuid.uuid4()), "name": "Gut Knife | Vanilla", "image": "images/skins/gut_knife_vanilla.png", "rarity": "rare_special", "case_id": "esports_2013"},
    
    # Operation Bravo Case
    {"id": str(uuid.uuid4()), "name": "AWP | Graphite", "image": "images/skins/awp_graphite.png", "rarity": "covert", "case_id": "bravo_case"},
    {"id": str(uuid.uuid4()), "name": "Desert Eagle | Golden Koi", "image": "images/skins/deagle_golden_koi.png", "rarity": "covert", "case_id": "bravo_case"},
    {"id": str(uuid.uuid4()), "name": "P90 | Emerald Dragon", "image": "images/skins/p90_emerald_dragon.png", "rarity": "classified", "case_id": "bravo_case"},
    {"id": str(uuid.uuid4()), "name": "P2000 | Ocean Foam", "image": "images/skins/p2000_ocean_foam.png", "rarity": "classified", "case_id": "bravo_case"},
    {"id": str(uuid.uuid4()), "name": "USP-S | Overgrowth", "image": "images/skins/usps_overgrowth.png", "rarity": "restricted", "case_id": "bravo_case"},
    {"id": str(uuid.uuid4()), "name": "M4A1-S | Bright Water", "image": "images/skins/m4a1s_bright_water.png", "rarity": "restricted", "case_id": "bravo_case"},
    {"id": str(uuid.uuid4()), "name": "M4A4 | Zirka", "image": "images/skins/m4a4_zirka.png", "rarity": "restricted", "case_id": "bravo_case"},
    {"id": str(uuid.uuid4()), "name": "Karambit | Vanilla", "image": "images/skins/karambit_vanilla.png", "rarity": "rare_special", "case_id": "bravo_case"},
    
    # Winter Offensive Weapon Case
    {"id": str(uuid.uuid4()), "name": "M4A4 | Asiimov", "image": "images/skins/m4a4_asiimov.png", "rarity": "covert", "case_id": "winter_offensive"},
    {"id": str(uuid.uuid4()), "name": "AWP | Redline", "image": "images/skins/awp_redline.png", "rarity": "classified", "case_id": "winter_offensive"},
    {"id": str(uuid.uuid4()), "name": "M4A1-S | Guardian", "image": "images/skins/m4a1s_guardian.png", "rarity": "classified", "case_id": "winter_offensive"},
    {"id": str(uuid.uuid4()), "name": "P250 | Mehndi", "image": "images/skins/p250_mehndi.png", "rarity": "restricted", "case_id": "winter_offensive"},
    {"id": str(uuid.uuid4()), "name": "Nova | Rising Skull", "image": "images/skins/nova_rising_skull.png", "rarity": "mil_spec", "case_id": "winter_offensive"},
    {"id": str(uuid.uuid4()), "name": "M9 Bayonet | Vanilla", "image": "images/skins/m9_bayonet_vanilla.png", "rarity": "rare_special", "case_id": "winter_offensive"},
    
    # Adding skins for 2014 cases
    # eSports 2013 Winter Case
    {"id": str(uuid.uuid4()), "name": "AWP | Corticera", "image": "images/skins/awp_corticera.png", "rarity": "classified", "case_id": "esports_winter"},
    {"id": str(uuid.uuid4()), "name": "AK-47 | Blue Laminate", "image": "images/skins/ak47_blue_laminate.png", "rarity": "restricted", "case_id": "esports_winter"},
    {"id": str(uuid.uuid4()), "name": "M4A4 | X-Ray", "image": "images/skins/m4a4_x_ray.png", "rarity": "covert", "case_id": "esports_winter"},
    {"id": str(uuid.uuid4()), "name": "P90 | Blind Spot", "image": "images/skins/p90_blind_spot.png", "rarity": "mil_spec", "case_id": "esports_winter"},
    {"id": str(uuid.uuid4()), "name": "Bayonet | Vanilla", "image": "images/skins/bayonet_vanilla.png", "rarity": "rare_special", "case_id": "esports_winter"},
    
    # CS:GO Weapon Case 3
    {"id": str(uuid.uuid4()), "name": "CZ75-Auto | Victoria", "image": "images/skins/cz75_victoria.png", "rarity": "covert", "case_id": "csgo_case_3"},
    {"id": str(uuid.uuid4()), "name": "P250 | Undertow", "image": "images/skins/p250_undertow.png", "rarity": "classified", "case_id": "csgo_case_3"},
    {"id": str(uuid.uuid4()), "name": "CZ75-Auto | The Fuschia Is Now", "image": "images/skins/cz75_fuschia.png", "rarity": "restricted", "case_id": "csgo_case_3"},
    {"id": str(uuid.uuid4()), "name": "USP-S | Stainless", "image": "images/skins/usps_stainless.png", "rarity": "mil_spec", "case_id": "csgo_case_3"},
    {"id": str(uuid.uuid4()), "name": "Huntsman Knife | Vanilla", "image": "images/skins/huntsman_vanilla.png", "rarity": "rare_special", "case_id": "csgo_case_3"},
    
    # And continuing for other cases...
    # Operation Phoenix Weapon Case
    {"id": str(uuid.uuid4()), "name": "AWP | Asiimov", "image": "images/skins/awp_asiimov.png", "rarity": "covert", "case_id": "phoenix_case"},
    {"id": str(uuid.uuid4()), "name": "AK-47 | Redline", "image": "images/skins/ak47_redline.png", "rarity": "classified", "case_id": "phoenix_case"},
    {"id": str(uuid.uuid4()), "name": "Nova | Antique", "image": "images/skins/nova_antique.png", "rarity": "restricted", "case_id": "phoenix_case"},
    {"id": str(uuid.uuid4()), "name": "MAC-10 | Heat", "image": "images/skins/mac10_heat.png", "rarity": "mil_spec", "case_id": "phoenix_case"},
    {"id": str(uuid.uuid4()), "name": "Butterfly Knife | Vanilla", "image": "images/skins/butterfly_vanilla.png", "rarity": "rare_special", "case_id": "phoenix_case"},
    
    # Operation Breakout Weapon Case
    {"id": str(uuid.uuid4()), "name": "M4A1-S | Cyrex", "image": "images/skins/m4a1s_cyrex.png", "rarity": "covert", "case_id": "breakout_case"},
    {"id": str(uuid.uuid4()), "name": "P90 | Asiimov", "image": "images/skins/p90_asiimov.png", "rarity": "classified", "case_id": "breakout_case"},
    {"id": str(uuid.uuid4()), "name": "Glock-18 | Water Elemental", "image": "images/skins/glock_water_elemental.png", "rarity": "restricted", "case_id": "breakout_case"},
    {"id": str(uuid.uuid4()), "name": "Desert Eagle | Conspiracy", "image": "images/skins/deagle_conspiracy.png", "rarity": "restricted", "case_id": "breakout_case"},
    {"id": str(uuid.uuid4()), "name": "Shadow Daggers | Vanilla", "image": "images/skins/shadow_daggers_vanilla.png", "rarity": "rare_special", "case_id": "breakout_case"},
    
    # 2015 Cases
    # Operation Vanguard Weapon Case
    {"id": str(uuid.uuid4()), "name": "AK-47 | Wasteland Rebel", "image": "images/skins/ak47_wasteland_rebel.png", "rarity": "covert", "case_id": "vanguard_case"},
    {"id": str(uuid.uuid4()), "name": "P2000 | Fire Elemental", "image": "images/skins/p2000_fire_elemental.png", "rarity": "classified", "case_id": "vanguard_case"},
    {"id": str(uuid.uuid4()), "name": "SCAR-20 | Cardiac", "image": "images/skins/scar20_cardiac.png", "rarity": "restricted", "case_id": "vanguard_case"},
    {"id": str(uuid.uuid4()), "name": "XM1014 | Tranquility", "image": "images/skins/xm1014_tranquility.png", "rarity": "mil_spec", "case_id": "vanguard_case"},
    {"id": str(uuid.uuid4()), "name": "Falchion Knife | Vanilla", "image": "images/skins/falchion_vanilla.png", "rarity": "rare_special", "case_id": "vanguard_case"},

    # Chroma Case
    {"id": str(uuid.uuid4()), "name": "AWP | Man-o'-war", "image": "images/skins/awp_man_o_war.png", "rarity": "covert", "case_id": "chroma_case"},
    {"id": str(uuid.uuid4()), "name": "AK-47 | Cartel", "image": "images/skins/ak47_cartel.png", "rarity": "classified", "case_id": "chroma_case"},
    {"id": str(uuid.uuid4()), "name": "M4A4 | 龍王 (Dragon King)", "image": "images/skins/m4a4_dragon_king.png", "rarity": "classified", "case_id": "chroma_case"},
    {"id": str(uuid.uuid4()), "name": "P250 | Muertos", "image": "images/skins/p250_muertos.png", "rarity": "restricted", "case_id": "chroma_case"},
    {"id": str(uuid.uuid4()), "name": "Bowie Knife | Vanilla", "image": "images/skins/bowie_knife_vanilla.png", "rarity": "rare_special", "case_id": "chroma_case"},
    
    # Falchion Case
    {"id": str(uuid.uuid4()), "name": "AK-47 | Aquamarine Revenge", "image": "images/skins/ak47_aquamarine_revenge.png", "rarity": "covert", "case_id": "falchion_case"},
    {"id": str(uuid.uuid4()), "name": "AWP | Hyper Beast", "image": "images/skins/awp_hyper_beast.png", "rarity": "covert", "case_id": "falchion_case"},
    {"id": str(uuid.uuid4()), "name": "SG 553 | Cyrex", "image": "images/skins/sg553_cyrex.png", "rarity": "classified", "case_id": "falchion_case"},
    {"id": str(uuid.uuid4()), "name": "MP7 | Nemesis", "image": "images/skins/mp7_nemesis.png", "rarity": "restricted", "case_id": "falchion_case"},
    {"id": str(uuid.uuid4()), "name": "Falchion Knife | Doppler", "image": "images/skins/falchion_doppler.png", "rarity": "rare_special", "case_id": "falchion_case"},
    
    # Shadow Case
    {"id": str(uuid.uuid4()), "name": "USP-S | Kill Confirmed", "image": "images/skins/usps_kill_confirmed.png", "rarity": "covert", "case_id": "shadow_case"},
    {"id": str(uuid.uuid4()), "name": "M4A1-S | Golden Coil", "image": "images/skins/m4a1s_golden_coil.png", "rarity": "covert", "case_id": "shadow_case"},
    {"id": str(uuid.uuid4()), "name": "AK-47 | Frontside Misty", "image": "images/skins/ak47_frontside_misty.png", "rarity": "classified", "case_id": "shadow_case"},
    {"id": str(uuid.uuid4()), "name": "G3SG1 | Flux", "image": "images/skins/g3sg1_flux.png", "rarity": "restricted", "case_id": "shadow_case"},
    {"id": str(uuid.uuid4()), "name": "Shadow Daggers | Fade", "image": "images/skins/shadow_daggers_fade.png", "rarity": "rare_special", "case_id": "shadow_case"},
    
    # Revolver Case
    {"id": str(uuid.uuid4()), "name": "R8 Revolver | Fade", "image": "images/skins/r8_fade.png", "rarity": "covert", "case_id": "revolver_case"},
    {"id": str(uuid.uuid4()), "name": "M4A4 | Royal Paladin", "image": "images/skins/m4a4_royal_paladin.png", "rarity": "covert", "case_id": "revolver_case"},
    {"id": str(uuid.uuid4()), "name": "AK-47 | Point Disarray", "image": "images/skins/ak47_point_disarray.png", "rarity": "classified", "case_id": "revolver_case"},
    {"id": str(uuid.uuid4()), "name": "G3SG1 | The Executioner", "image": "images/skins/g3sg1_executioner.png", "rarity": "restricted", "case_id": "revolver_case"},
    {"id": str(uuid.uuid4()), "name": "Bowie Knife | Crimson Web", "image": "images/skins/bowie_crimson_web.png", "rarity": "rare_special", "case_id": "revolver_case"},
    
    # 2016 Cases
    # Chroma 2 Case
    {"id": str(uuid.uuid4()), "name": "M4A1-S | Hyper Beast", "image": "images/skins/m4a1s_hyper_beast.png", "rarity": "covert", "case_id": "chroma_2_case"},
    {"id": str(uuid.uuid4()), "name": "AK-47 | Elite Build", "image": "images/skins/ak47_elite_build.png", "rarity": "classified", "case_id": "chroma_2_case"},
    {"id": str(uuid.uuid4()), "name": "AWP | Worm God", "image": "images/skins/awp_worm_god.png", "rarity": "restricted", "case_id": "chroma_2_case"},
    {"id": str(uuid.uuid4()), "name": "Five-SeveN | Monkey Business", "image": "images/skins/fiveseven_monkey_business.png", "rarity": "mil_spec", "case_id": "chroma_2_case"},
    {"id": str(uuid.uuid4()), "name": "Karambit | Doppler", "image": "images/skins/karambit_doppler.png", "rarity": "rare_special", "case_id": "chroma_2_case"},
    
    # Gamma Case
    {"id": str(uuid.uuid4()), "name": "M4A1-S | Mecha Industries", "image": "images/skins/m4a1s_mecha_industries.png", "rarity": "covert", "case_id": "gamma_case"},
    {"id": str(uuid.uuid4()), "name": "Glock-18 | Wasteland Rebel", "image": "images/skins/glock_wasteland_rebel.png", "rarity": "classified", "case_id": "gamma_case"},
    {"id": str(uuid.uuid4()), "name": "M4A4 | Desolate Space", "image": "images/skins/m4a4_desolate_space.png", "rarity": "classified", "case_id": "gamma_case"},
    {"id": str(uuid.uuid4()), "name": "P2000 | Imperial Dragon", "image": "images/skins/p2000_imperial_dragon.png", "rarity": "restricted", "case_id": "gamma_case"},
    {"id": str(uuid.uuid4()), "name": "Flip Knife | Gamma Doppler", "image": "images/skins/flip_knife_gamma_doppler.png", "rarity": "rare_special", "case_id": "gamma_case"},
    
    # Gamma 2 Case
    {"id": str(uuid.uuid4()), "name": "AK-47 | Neon Revolution", "image": "images/skins/ak47_neon_revolution.png", "rarity": "covert", "case_id": "gamma_2_case"},
    {"id": str(uuid.uuid4()), "name": "FAMAS | Roll Cage", "image": "images/skins/famas_roll_cage.png", "rarity": "classified", "case_id": "gamma_2_case"},
    {"id": str(uuid.uuid4()), "name": "Tec-9 | Fuel Injector", "image": "images/skins/tec9_fuel_injector.png", "rarity": "classified", "case_id": "gamma_2_case"},
    {"id": str(uuid.uuid4()), "name": "MAG-7 | Petroglyph", "image": "images/skins/mag7_petroglyph.png", "rarity": "restricted", "case_id": "gamma_2_case"},
    {"id": str(uuid.uuid4()), "name": "M9 Bayonet | Gamma Doppler", "image": "images/skins/m9_bayonet_gamma_doppler.png", "rarity": "rare_special", "case_id": "gamma_2_case"},
    
    # 2017 Cases
    # Glove Case
    {"id": str(uuid.uuid4()), "name": "M4A4 | Buzz Kill", "image": "images/skins/m4a4_buzz_kill.png", "rarity": "covert", "case_id": "glove_case"},
    {"id": str(uuid.uuid4()), "name": "SCAR-20 | Bloodsport", "image": "images/skins/scar20_bloodsport.png", "rarity": "classified", "case_id": "glove_case"},
    {"id": str(uuid.uuid4()), "name": "P90 | Shallow Grave", "image": "images/skins/p90_shallow_grave.png", "rarity": "restricted", "case_id": "glove_case"},
    {"id": str(uuid.uuid4()), "name": "Dual Berettas | Royal Consorts", "image": "images/skins/dual_berettas_royal_consorts.png", "rarity": "mil_spec", "case_id": "glove_case"},
    {"id": str(uuid.uuid4()), "name": "Hand Wraps | Leather", "image": "images/skins/hand_wraps_leather.png", "rarity": "rare_special", "case_id": "glove_case"},
    
    # Spectrum Case
    {"id": str(uuid.uuid4()), "name": "AK-47 | Bloodsport", "image": "images/skins/ak47_bloodsport.png", "rarity": "covert", "case_id": "spectrum_case"},
    {"id": str(uuid.uuid4()), "name": "USP-S | Neo-Noir", "image": "images/skins/usps_neo_noir.png", "rarity": "covert", "case_id": "spectrum_case"},
    {"id": str(uuid.uuid4()), "name": "AWP | Fever Dream", "image": "images/skins/awp_fever_dream.png", "rarity": "classified", "case_id": "spectrum_case"},
    {"id": str(uuid.uuid4()), "name": "M4A1-S | Decimator", "image": "images/skins/m4a1s_decimator.png", "rarity": "classified", "case_id": "spectrum_case"},
    {"id": str(uuid.uuid4()), "name": "Butterfly Knife | Marble Fade", "image": "images/skins/butterfly_marble_fade.png", "rarity": "rare_special", "case_id": "spectrum_case"},
    
    # Operation Hydra Case
    {"id": str(uuid.uuid4()), "name": "AWP | Oni Taiji", "image": "images/skins/awp_oni_taiji.png", "rarity": "covert", "case_id": "hydra_case"},
    {"id": str(uuid.uuid4()), "name": "Five-SeveN | Hyper Beast", "image": "images/skins/fiveseven_hyper_beast.png", "rarity": "classified", "case_id": "hydra_case"},
    {"id": str(uuid.uuid4()), "name": "M4A4 | Hellfire", "image": "images/skins/m4a4_hellfire.png", "rarity": "classified", "case_id": "hydra_case"},
    {"id": str(uuid.uuid4()), "name": "Dual Berettas | Cobra Strike", "image": "images/skins/dual_berettas_cobra_strike.png", "rarity": "restricted", "case_id": "hydra_case"},
    {"id": str(uuid.uuid4()), "name": "Driver Gloves | Lunar Weave", "image": "images/skins/driver_gloves_lunar_weave.png", "rarity": "rare_special", "case_id": "hydra_case"},
    
    # Spectrum 2 Case
    {"id": str(uuid.uuid4()), "name": "AK-47 | The Empress", "image": "images/skins/ak47_the_empress.png", "rarity": "covert", "case_id": "spectrum_2_case"},
    {"id": str(uuid.uuid4()), "name": "P250 | See Ya Later", "image": "images/skins/p250_see_ya_later.png", "rarity": "covert", "case_id": "spectrum_2_case"},
    {"id": str(uuid.uuid4()), "name": "M4A1-S | Leaded Glass", "image": "images/skins/m4a1s_leaded_glass.png", "rarity": "classified", "case_id": "spectrum_2_case"},
    {"id": str(uuid.uuid4()), "name": "XM1014 | Ziggy", "image": "images/skins/xm1014_ziggy.png", "rarity": "restricted", "case_id": "spectrum_2_case"},
    {"id": str(uuid.uuid4()), "name": "Sport Gloves | Omega", "image": "images/skins/sport_gloves_omega.png", "rarity": "rare_special", "case_id": "spectrum_2_case"}
]

# Define cases
cases = [
    # First cases
    {
        "id": "csgo_case_1",
        "name": "CS:GO Weapon Case",
        "image": "images/cases/csgo_case_1.png",
        "price": 250,
        "year": "2013",
        "description": "The original CS:GO weapon case featuring the AWP | Lightning Strike."
    },
    {
        "id": "csgo_case_2",
        "name": "CS:GO Weapon Case 2",
        "image": "images/cases/csgo_case_2.png",
        "price": 250,
        "year": "2013",
        "description": "The second CS:GO weapon case featuring the SSG 08 | Blood in the Water."
    },
    {
        "id": "esports_2013",
        "name": "eSports 2013 Case",
        "image": "images/cases/esports_2013.png",
        "price": 250,
        "year": "2013",
        "description": "The eSports 2013 case featuring the P90 | Death by Kitty."
    },
    {
        "id": "bravo_case",
        "name": "Operation Bravo Case",
        "image": "images/cases/bravo_case.png",
        "price": 300,
        "year": "2013",
        "description": "The Operation Bravo case featuring the AWP | Graphite."
    },
    {
        "id": "winter_offensive",
        "name": "Winter Offensive Weapon Case",
        "image": "images/cases/winter_offensive.png",
        "price": 250,
        "year": "2013",
        "description": "The Winter Offensive case featuring the M4A4 | Asiimov."
    },
    
    # 2014 cases
    {
        "id": "esports_winter",
        "name": "eSports 2013 Winter Case",
        "image": "images/cases/esports_winter.png",
        "price": 250,
        "year": "2014",
        "description": "The eSports Winter case featuring the M4A4 | X-Ray."
    },
    {
        "id": "csgo_case_3",
        "name": "CS:GO Weapon Case 3",
        "image": "images/cases/csgo_case_3.png",
        "price": 250,
        "year": "2014",
        "description": "The third CS:GO weapon case featuring the CZ75-Auto | Victoria."
    },
    {
        "id": "phoenix_case",
        "name": "Operation Phoenix Weapon Case",
        "image": "images/cases/phoenix_case.png",
        "price": 250,
        "year": "2014",
        "description": "The Operation Phoenix case featuring the AWP | Asiimov."
    },
    {
        "id": "huntsman_case",
        "name": "Huntsman Weapon Case",
        "image": "images/cases/huntsman_case.png",
        "price": 250,
        "year": "2014",
        "description": "The Huntsman case featuring the AK-47 | Vulcan."
    },
    {
        "id": "breakout_case",
        "name": "Operation Breakout Weapon Case",
        "image": "images/cases/breakout_case.png",
        "price": 250,
        "year": "2014",
        "description": "The Operation Breakout case featuring the M4A1-S | Cyrex."
    },
    {
        "id": "esports_summer",
        "name": "eSports 2014 Summer Case",
        "image": "images/cases/esports_summer.png",
        "price": 250,
        "year": "2014",
        "description": "The eSports Summer case featuring the M4A4 | Bullet Rain."
    },
    
    # 2015 cases
    {
        "id": "vanguard_case",
        "name": "Operation Vanguard Weapon Case",
        "image": "images/cases/vanguard_case.png",
        "price": 250,
        "year": "2015",
        "description": "The Operation Vanguard case featuring the AK-47 | Wasteland Rebel."
    },
    {
        "id": "chroma_case",
        "name": "Chroma Case",
        "image": "images/cases/chroma_case.png",
        "price": 250,
        "year": "2015",
        "description": "The Chroma case featuring the AWP | Man-o'-war."
    },
    {
        "id": "falchion_case",
        "name": "Falchion Case",
        "image": "images/cases/falchion_case.png",
        "price": 250,
        "year": "2015",
        "description": "The Falchion case featuring the AK-47 | Aquamarine Revenge."
    },
    {
        "id": "shadow_case",
        "name": "Shadow Case",
        "image": "images/cases/shadow_case.png",
        "price": 250,
        "year": "2015",
        "description": "The Shadow case featuring the USP-S | Kill Confirmed."
    },
    {
        "id": "revolver_case",
        "name": "Revolver Case",
        "image": "images/cases/revolver_case.png",
        "price": 250,
        "year": "2015",
        "description": "The Revolver case featuring the R8 Revolver | Fade."
    },
    
    # 2016 cases
    {
        "id": "chroma_2_case",
        "name": "Chroma 2 Case",
        "image": "images/cases/chroma_2_case.png",
        "price": 250,
        "year": "2016",
        "description": "The Chroma 2 case featuring the M4A1-S | Hyper Beast."
    },
    {
        "id": "gamma_case",
        "name": "Gamma Case",
        "image": "images/cases/gamma_case.png",
        "price": 250,
        "year": "2016",
        "description": "The Gamma case featuring the M4A1-S | Mecha Industries."
    },
    {
        "id": "gamma_2_case",
        "name": "Gamma 2 Case",
        "image": "images/cases/gamma_2_case.png",
        "price": 250,
        "year": "2016",
        "description": "The Gamma 2 case featuring the AK-47 | Neon Revolution."
    },
    
    # 2017 cases
    {
        "id": "glove_case",
        "name": "Glove Case",
        "image": "images/cases/glove_case.png",
        "price": 250,
        "year": "2017",
        "description": "The Glove case featuring the M4A4 | Buzz Kill and special glove skins."
    },
    {
        "id": "spectrum_case",
        "name": "Spectrum Case",
        "image": "images/cases/spectrum_case.png",
        "price": 250,
        "year": "2017",
        "description": "The Spectrum case featuring the AK-47 | Bloodsport."
    },
    {
        "id": "hydra_case",
        "name": "Operation Hydra Case",
        "image": "images/cases/hydra_case.png",
        "price": 250,
        "year": "2017",
        "description": "The Operation Hydra case featuring the AWP | Oni Taiji."
    },
    {
        "id": "spectrum_2_case",
        "name": "Spectrum 2 Case",
        "image": "images/cases/spectrum_2_case.png",
        "price": 250,
        "year": "2017",
        "description": "The Spectrum 2 case featuring the AK-47 | The Empress."
    }
]

# Insert data to MongoDB
db.cases.insert_many(cases)
db.items.insert_many(weapons)
for rarity_key, rarity_data in rarities.items():
    db.rarities.insert_one({"id": rarity_key, "name": rarity_data["name"], "color": rarity_data["color"]})

print("Database initialized successfully with:")
print(f"- {len(cases)} cases")
print(f"- {len(weapons)} weapon skins")
print(f"- {len(rarities)} rarity levels")

# Create indexes for performance
db.items.create_index("case_id")
db.items.create_index("rarity")
db.users.create_index("steamId", unique=True)

print("Database indexes created successfully!")