from process_config import RIM,ANODIZING,PHYSICS
def area_dm2(): return RIM["surface_area_in2"]*0.064516
def required_current_a(): return ANODIZING["current_density_a_dm2"]*area_dm2()
def current_density(i): return i/area_dm2() if area_dm2() else 0
def power_kw(v,i): return v*i/1000
def oxide_growth_um(i,seconds,eff=None):
    eff=ANODIZING["current_efficiency"] if eff is None else eff
    area=RIM["surface_area_in2"]*0.00064516
    mass_area=i*seconds*PHYSICS["oxide_molar_mass_kg_mol"]*eff/(PHYSICS["electrons_per_mole_oxide"]*PHYSICS["faraday"])
    return max(0,mass_area/PHYSICS["oxide_density_kg_m3"]/area*1e6)
def predicted_final_thickness(current,i,remaining):
    return min(ANODIZING["max_thickness_um"],current+oxide_growth_um(i,remaining))
